# nodes.py
# nodes.py (FeatureTree + ε-greedy + VersionStore + metrics++ + preprocess/type-guard + Tavily plugin + hybrid/rerank)

import os, time, random
from dotenv import load_dotenv
load_dotenv()

from typing import List, Dict, Optional, Any, Tuple
from concurrent.futures import ThreadPoolExecutor

from langchain_core.documents import Document
from langchain_core.messages import HumanMessage, SystemMessage

from state import State
from db import get_vectorstore, get_llm, extract_section_terms
from rpg import (
    configure_rag_for_context,
    RAGComponentRegistry,
    DataFlowManager,
    unit_test_flow_assertions,
    bind_registry_to_hints,
    LegalRetrievalPlugin,
    FeatureTree, FeatureTreeNode,
    RPGVersionStore, merge_rpg,
)

from policy import EPSILON

# Shared DataFlowManager & thread pool (IO-bound tasks)
_DFM = DataFlowManager()
_EXEC = ThreadPoolExecutor(max_workers=int(os.getenv("RAG_MAX_WORKERS", "4")))
_STORE = RPGVersionStore(root_dir=os.getenv("RPG_STORE_DIR"))

# ---------------- Tavily web search (optional) ----------------
def _web_search_tavily(query: str, k: int = 5) -> List[Document]:
    """
    Lightweight Tavily wrapper with lazy import and env gating.
    Requires:
    - ENABLE_TAVILY=1
    - TAVILY_API_KEY set
    """
    if not query or os.getenv("ENABLE_TAVILY", "0").lower() in ("0", "false", "no"):
        return []
    try:
        from tavily import TavilyClient  # provided by tavily-python
    except Exception:
        return []
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        return []
    try:
        client = TavilyClient(api_key=api_key)
        resp = client.search(query)
    except Exception:
        return []
    docs: List[Document] = []
    for r in (resp.get("results") or [])[: max(1, k)]:
        url = r.get("url") or "unknown"
        text = (r.get("content") or r.get("title") or "").strip()
        if not text:
            continue
        md = {"source": url, "url": url, "ext": ".html", "score": float(r.get("score") or 0.0)}
        docs.append(Document(page_content=text, metadata=md))
    return docs

# ---------------- Preprocess & type guards ----------------
def _dfm_fill_defaults(frm: str, to: str, st: Dict[str, Any]) -> Dict[str, Any]:
    out = dict(st or {})
    out.setdefault("retrieval_hints", {"k": 8, "strategy": "semantic"})
    out.setdefault("plugins", [])
    out.setdefault("log", [])
    out.setdefault("documents", [])
    enable = str(os.getenv("RAG_CITATIONS", "1")).lower() not in ("0", "false", "no")
    max_n = int(os.getenv("RAG_CITATIONS_MAX", "8"))
    out.setdefault(
        "citation_policy",
        {
            "enable": enable,
            "max": max_n,
            "inline": True,
            "append_section": True,
            "label": os.getenv("RAG_CITATIONS_LABEL", "출처"),
        },
    )
    out.setdefault("sources", [])
    return out

def _dfm_stringify_query(frm: str, to: str, st: Dict[str, Any]) -> Dict[str, Any]:
    out = dict(st or {})
    q = out.get("refined_query") or out.get("query")
    if q is not None and not isinstance(q, str):
        out["refined_query"] = str(q)
    return out

_DFM.add_preprocess(_dfm_fill_defaults)
_DFM.add_preprocess(_dfm_stringify_query)

# ---------------- Utilities ----------------
def _append_flow_violations(state: State, frm: str, to: str, snapshot: Dict[str, Any]) -> List[Dict[str, Any]]:
    res = _DFM.validate(frm, to, snapshot)
    violations = (state.get("flow_violations") or [])[:]
    if not res.get("ok"):
        for v in res.get("violations", []):
            violations.append({"from": frm, "to": to, "error": v})
    return violations

def _get_question(state: State) -> str:
    msgs = state.get("messages") or []
    for m in reversed(list(msgs)):
        content = None; role = None
        if hasattr(m, "content"):
            content = getattr(m, "content", None)
            role = getattr(m, "type", None) or getattr(m, "role", None)
        if isinstance(m, dict):
            content = m.get("content")
            role = m.get("type") or m.get("role")
        if role in ("human", "user") and isinstance(content, str) and content.strip():
            return content.strip()
    return (state.get("query") or "").strip()

def _infer_context_type(q: str) -> str:
    ql = q.lower()
    if any(k in ql for k in ["법", "판례", "조항", "legal", "contract", "compliance"]):
        return "legal"
    if any(k in ql for k in ["code", "function", "error", "stack", "api", "기술", "기능", "스택", "버그"]):
        return "technical"
    if any(k in ql for k in ["대화", "챗봇", "상담", "chat", "conversation"]):
        return "conversational"
    return "general"

def _source_diversity(docs_: List[Document]) -> float:
    if not docs_:
        return 0.0
    sources = set()
    for d in docs_:
        meta = getattr(d, "metadata", {}) or {}
        src = meta.get("source") or meta.get("file") or meta.get("url") or "unknown"
        sources.add(src)
    return round(len(sources) / max(1, len(docs_)), 3)

def _intent_coverage(docs: List[Document], query: str) -> float:
    terms = extract_section_terms(query) or []
    if not terms or not docs:
        return 0.0 if not docs else 0.5
    hits = 0
    for d in docs:
        ns_terms = (d.metadata or {}).get("ns_terms") or []
        if any(t in ns_terms for t in terms):
            hits += 1
    return round(hits / max(1, len(docs)), 3)

def _negative_rate(docs: List[Document]) -> float:
    if not docs:
        return 1.0
    scores = [float((d.metadata or {}).get("score") or 0.0) for d in docs]
    negs = sum(1 for s in scores if s <= 0.0)
    return round(negs / max(1, len(scores)), 3)

def _novel_contrib(current: List[Document], prev: List[Document]) -> float:
    prev_src = set((d.metadata or {}).get("source") for d in prev or [])
    cur_src = set((d.metadata or {}).get("source") for d in current or [])
    if not cur_src:
        return 0.0
    novel = len([s for s in cur_src if s not in prev_src])
    return round(novel / max(1, len(cur_src)), 3)

def _calc_metrics(docs: List[Document], k: int, query: str, prev_docs: Optional[List[Document]] = None) -> Dict[str, Any]:
    n = len(docs)
    scores = [
        float((d.metadata or {}).get("score") or 0.0)
        for d in docs
        if isinstance((d.metadata or {}).get("score"), (int, float))
    ]
    avg_score = round(sum(scores) / len(scores), 4) if scores else 0.0
    coverage = round(min(1.0, n / max(1, k)), 3)
    diversity = _source_diversity(docs)
    intent_cov = _intent_coverage(docs, query)
    neg_rate = _negative_rate(docs)
    novel_contrib = _novel_contrib(docs, prev_docs or [])
    return {
        "k": k,
        "n": n,
        "avg_score": avg_score,
        "coverage": coverage,
        "diversity": diversity,
        "intent_coverage": intent_cov,
        "negative_rate": neg_rate,
        "novel_evidence_contrib": novel_contrib,
    }

def _run_vs_search(vs, q: str, k: int, meta_filter: Optional[Dict[str, Any]] = None) -> List[Tuple[Document, float]]:
    fut = _EXEC.submit(vs.similarity_search_with_score, q, k, None, meta_filter)
    return fut.result()

def _merge_scored_docs(pairs: List[Tuple[Document, float]], seen: set) -> List[Document]:
    out: List[Document] = []
    for d, s in pairs:
        key = (d.page_content.strip()[:120], (d.metadata or {}).get("source", ""))
        if key in seen:
            continue
        seen.add(key)
        md = dict(d.metadata or {})
        md["score"] = float(s)
        d.metadata = md
        out.append(d)
    return out

def _now() -> float:
    return time.time()

def _apply_rpg_subgraph_filter(docs: List[Document], state: State) -> List[Document]:
    ctx = state.get("context_type") or "general"
    q = state.get("refined_query") or state.get("query") or ""
    q_terms = extract_section_terms(q) or []
    kept: List[Document] = []
    for d in docs:
        md = d.metadata or {}
        ext = (md.get("ext") or "").lower()
        ns_terms = md.get("ns_terms") or []
        ok = True
        if ctx == "legal":
            ok = (any(t in ns_terms for t in q_terms) if q_terms else ext in [".pdf", ".docx", ".md", ".txt"])
        elif ctx == "technical":
            # .txt 포함 및 코드/구성 포맷 허용
            ok = ext in [".py", ".ipynb", ".md", ".rst", ".json", ".yaml", ".yml", ".toml", ".txt"]
        elif ctx == "conversational":
            ok = ext in [".md", ".txt", ".html", ".htm"]
        if ok:
            kept.append(d)
    # 필터 결과가 0개면 우회하여 원본 반환
    return kept if kept else docs

def _thread_id(state: State) -> str:
    return (state.get("thread_id") or os.getenv("THREAD_ID") or "default")

def _unique_sources(docs: List[Document], limit: int = 10) -> List[str]:
    uniq: List[str] = []
    seen = set()
    for d in docs:
        md = d.metadata or {}
        src = md.get("source") or md.get("url") or md.get("file") or "unknown"
        if src not in seen:
            seen.add(src)
            uniq.append(src)
        if len(uniq) >= max(1, limit):
            break
    return uniq

def _render_sources_section(sources: List[str], label: str = "출처") -> str:
    if not sources:
        return ""
    lines = [f"{label}:"]
    for i, s in enumerate(sources, 1):
        lines.append(f"[{i}] {s}")
    return "\n".join(lines)

def _simple_keyword_score(text: str, query: str) -> float:
    if not text or not query:
        return 0.0
    q_terms = [t for t in query.lower().split() if len(t) > 1]
    tl = text.lower()
    return float(sum(tl.count(t) for t in q_terms))

# ---------------- Compose RPG ----------------
def compose_rpg(state: State) -> Dict[str, Any]:
    q = (_get_question(state) or state.get("refined_query") or state.get("query") or "").strip()
    context_type = _infer_context_type(q)
    rpg_graph = configure_rag_for_context(context_type, q)

    registry_obj = RAGComponentRegistry()
    registry = registry_obj.to_dict()

    hints = bind_registry_to_hints(registry, context_type, base_hints=state.get("retrieval_hints") or {})
    plugins = list(state.get("plugins") or [])
    if context_type == "legal":
        leg = LegalRetrievalPlugin()
        plug_out = leg.execute({"retrieval_hints": hints, "plugins": plugins})
        hints = plug_out.get("retrieval_hints", hints)
        plugins = plug_out.get("plugins", plugins)

    execution_path = rpg_graph.suggest_execution_path(state.get("retrieval_metrics"))
    rpg_dict = rpg_graph.to_dict()
    ver = _STORE.save(rpg_dict, note=f"context={context_type}")

    log = (state.get("log") or []) + [{"at": "compose_rpg", "ts": _now(), "context": context_type, "ver": ver}]
    out = {
        "query": q or state.get("query") or "",
        "context_type": context_type,
        "rpg": {"graph": rpg_dict, "registry": registry, "flows": []},
        "retrieval_hints": hints,
        "plugins": plugins,
        "execution_path": execution_path,
        "phase": "setup",
        "log": log,
        "rpg_version": ver,
        "rpg_versions": (state.get("rpg_versions") or []) + [{"version": ver, "ts": _now(), "note": f"context={context_type}"}],
    }

    snap = _DFM.preprocess("compose_rpg", "intent_parser", {**(state or {}), **out})
    out["flow_violations"] = _append_flow_violations(state, "compose_rpg", "intent_parser", snap)
    return out

# ---------------- Intent parsing ----------------
def intent_parser(state: State) -> Dict[str, Any]:
    q = (_get_question(state) or state.get("query") or "").strip()
    refined = q
    hints = dict(state.get("retrieval_hints") or {})
    out = {"refined_query": refined, "retrieval_hints": hints, "phase": "refine"}
    snap = _DFM.preprocess("intent_parser", "retrieve_rpg", {**(state or {}), **out})
    out["flow_violations"] = _append_flow_violations(state, "intent_parser", "retrieve_rpg", snap)
    return out

# ---------------- Retrieval (hybrid-ready) ----------------
def retrieve_rpg(state: State) -> Dict[str, Any]:
    q = state.get("refined_query") or state.get("query") or ""
    hints = dict(state.get("retrieval_hints") or {})
    k = int(hints.get("k", 8))

    meta_filter: Dict[str, Any] = {}
    if hints.get("section_boost"):
        meta_filter["ext"] = {"$in": [".pdf", ".docx", ".md", ".txt"]}

    # paths 힌트 전달
    vs = get_vectorstore(auto_bootstrap=True, file_paths=hints.get("paths"))

    dense_pairs = _run_vs_search(vs, q, k, meta_filter or None)
    seen = set()
    docs = _merge_scored_docs(dense_pairs, seen)

    # Hybrid weighting stub
    bm25_w = float(hints.get("bm25_weight", 0.0) or 0.0)
    dense_w = float(hints.get("dense_weight", 1.0) or 1.0)
    if bm25_w > 0.0:
        for d in docs:
            kw = _simple_keyword_score(d.page_content or "", q)
            md = dict(d.metadata or {})
            dense_s = float(md.get("score") or 0.0)
            md["bm25_score"] = kw
            md["hybrid_score"] = bm25_w * kw + dense_w * dense_s
            d.metadata = md
        # sort by hybrid_score if available
        docs.sort(key=lambda d: (d.metadata or {}).get("hybrid_score", (d.metadata or {}).get("score", 0.0)), reverse=True)

    docs = _apply_rpg_subgraph_filter(docs, state)

    # Tavily mix-in
    web_docs = _web_search_tavily(q, k=max(3, k // 2))
    if web_docs:
        mixed = list(docs) + web_docs
        uniq: List[Document] = []
        seen_src = set()
        for d in mixed:
            src = (d.metadata or {}).get("source")
            if src in seen_src:
                continue
            seen_src.add(src)
            # ensure ext default for web
            md = dict(d.metadata or {})
            md["ext"] = md.get("ext") or ".html"
            d.metadata = md
            uniq.append(d)
        docs = _apply_rpg_subgraph_filter(uniq, state)

    metrics = _calc_metrics(docs, k, q, prev_docs=None)
    log = (state.get("log") or []) + [{"at": "retrieve_rpg", "n": len(docs), "ts": _now()}]
    out = {"documents": docs, "retrieval_metrics": metrics, "phase": "search", "log": log}
    snap = _DFM.preprocess("retrieve_rpg", "award_xp", {**(state or {}), **out})
    out["flow_violations"] = _append_flow_violations(state, "retrieve_rpg", "award_xp", snap)
    return out

# ---------------- Award XP (new) ----------------
def award_xp(state: State) -> Dict[str, Any]:
    """
    Simple XP assignment node based on retrieval_metrics.
    Keeps epsilon available for future exploration logic.
    """
    metrics = dict(state.get("retrieval_metrics") or {})
    coverage = float(metrics.get("coverage") or 0.0)
    diversity = float(metrics.get("diversity") or 0.0)
    intent_cov = float(metrics.get("intent_coverage") or 0.0)
    neg = float(metrics.get("negative_rate") or 1.0)

    # Heuristic XP: reward good coverage/diversity/intent, penalize negatives
    xp = max(0.0, 2.5 * coverage + 2.0 * diversity + 2.0 * intent_cov - 1.5 * neg)
    xp = round(xp, 3)

    # Optional epsilon use (hook)
    explore = random.random() < float(EPSILON or 0.0)

    log = (state.get("log") or []) + [{"at": "award_xp", "xp": xp, "explore": explore, "ts": _now()}]
    out = {
        "xp": xp,
        "explore": explore,
        "log": log,
        "phase": "score",
        "metrics_history": (state.get("metrics_history") or []) + [metrics],
    }
    # No preprocess to next here because next hop is conditional; DataFlowManager hook can be added per edge if desired
    return out

# ---------------- Expand search ----------------
def expand_search(state: State) -> Dict[str, Any]:
    q = state.get("refined_query") or state.get("query") or ""
    hints = dict(state.get("retrieval_hints") or {})
    base_k = int(hints.get("k", 8))
    k = max(base_k, int(base_k * 2))

    vs = get_vectorstore(auto_bootstrap=False)
    pairs = _run_vs_search(vs, q, k, None)

    seen = set(((d.page_content.strip()[:120], (d.metadata or {}).get("source", "")) for d in state.get("documents") or []))
    new_docs = _merge_scored_docs(pairs, seen)

    # Tavily mix-in with lower ratio
    web_docs = _web_search_tavily(q, k=max(2, int(k * 0.4)))
    joined = list(new_docs) + (web_docs or [])

    # Dedupe by content prefix + source
    uniq2, seen2 = [], set()
    for d in joined:
        sig = ((d.page_content or "")[:120], (d.metadata or {}).get("source"))
        if sig in seen2:
            continue
        seen2.add(sig)
        md = dict(d.metadata or {})
        md["ext"] = md.get("ext") or ".html"
        d.metadata = md
        uniq2.append(d)

    docs = (state.get("documents") or []) + uniq2
    docs = _apply_rpg_subgraph_filter(docs, state)

    metrics = _calc_metrics(docs, k, q, prev_docs=state.get("documents") or [])
    log = (state.get("log") or []) + [{"at": "expand_search", "n": len(uniq2), "ts": _now()}]
    out = {"documents": docs, "retrieval_metrics": metrics, "phase": "search+", "log": log}

    snap = _DFM.preprocess("expand_search", "rerank", {**(state or {}), **out})
    out["flow_violations"] = _append_flow_violations(state, "expand_search", "rerank", snap)
    return out

# ---------------- Rerank (new) ----------------
def rerank(state: State) -> Dict[str, Any]:
    q = state.get("refined_query") or state.get("query") or ""
    docs: List[Document] = list(state.get("documents") or [])

    # Compute a simple keyword score if missing
    for d in docs:
        md = dict(d.metadata or {})
        if "bm25_score" not in md:
            md["bm25_score"] = _simple_keyword_score(d.page_content or "", q)
        d.metadata = md

    # Sort priority: hybrid_score > score > bm25_score
    def _key(d: Document):
        md = d.metadata or {}
        return (
            float(md.get("hybrid_score") or -1.0),
            float(md.get("score") or -1.0),
            float(md.get("bm25_score") or 0.0),
        )

    docs.sort(key=_key, reverse=True)

    # Keep top-N
    top_n = int(os.getenv("RERANK_TOPK", "12"))
    docs = docs[: max(1, top_n)]

    sources = _unique_sources(docs, limit=int(os.getenv("CITE_MAX", "10")))
    log = (state.get("log") or []) + [{"at": "rerank", "n": len(docs), "ts": _now()}]
    out = {
        "documents": docs,
        "sources": sources,
        "phase": "select",
        "log": log,
    }

    snap = _DFM.preprocess("rerank", "plan_answer", {**(state or {}), **out})
    out["flow_violations"] = _append_flow_violations(state, "rerank", "plan_answer", snap)
    return out

# ---------------- Plan answer (new) ----------------
def plan_answer(state: State) -> Dict[str, Any]:
    q = state.get("refined_query") or state.get("query") or ""
    docs: List[Document] = list(state.get("documents") or [])
    ctx = state.get("context_type") or "general"

    outline = [
        f"질문 재진술 및 맥락({ctx})",
        "핵심 요점 요약",
        "근거와 인용",
        "한계와 주의사항",
        "다음 단계 제안",
    ]
    # Very lightweight LLM-assisted refinement optional
    if os.getenv("ENABLE_PLAN_LLM", "0").lower() in ("1", "true", "yes"):
        llm = get_llm(role="router")
        sys = SystemMessage(content="아래 질의와 참고 문서를 바탕으로 한국어 답변 아웃라인을 3~6개 항목으로 간결하게 만드세요.")
        user = HumanMessage(content=f"질의: {q}\n참고 문서 수: {len(docs)}")
        try:
            resp = llm.invoke([sys, user])
            txt = (getattr(resp, "content", None) or "").strip()
            if txt:
                outline = [line.strip("-• ").strip() for line in txt.splitlines() if line.strip()]
                outline = [o for o in outline if o]
        except Exception:
            pass

    plan = {"outline": outline, "style": "concise_kr"}
    log = (state.get("log") or []) + [{"at": "plan_answer", "ts": _now()}]
    out = {"plan": plan, "phase": "plan", "log": log}

    snap = _DFM.preprocess("plan_answer", "generate_answer", {**(state or {}), **out})
    out["flow_violations"] = _append_flow_violations(state, "plan_answer", "generate_answer", snap)
    return out

# ---------------- Generate answer (new) ----------------
def generate_answer(state: State) -> Dict[str, Any]:
    q = state.get("refined_query") or state.get("query") or ""
    docs: List[Document] = list(state.get("documents") or [])
    sources: List[str] = list(state.get("sources") or _unique_sources(docs))
    plan = state.get("plan") or {}
    cite_cfg = state.get("citation_policy") or {}
    label = str(cite_cfg.get("label") or "출처")
    add_section = bool(cite_cfg.get("append_section", True))
    inline = bool(cite_cfg.get("inline", True))

    # Build context block
    ctx_snippets = []
    max_ctx = int(os.getenv("GEN_MAX_CTX_SNIPPETS", "6"))
    for d in docs[:max_ctx]:
        src = (d.metadata or {}).get("source") or ""
        ctx_snippets.append(f"[{src}] {d.page_content[:400]}")

    system_prompt = (
        "다음 지침을 따르세요:\n"
        "- 질문에 정확하고 간결하게 한국어로 답변합니다.\n"
        "- 제공된 컨텍스트만을 근거로 하며, 불확실하면 한계를 명시합니다.\n"
        "- 요구 시 출처를 제공합니다."
    )
    outline_lines = []
    for i, sec in enumerate((plan.get("outline") or []), 1):
        outline_lines.append(f"{i}. {sec}")
    outline_block = "\n".join(outline_lines) if outline_lines else ""

    llm = get_llm(role="gen")
    sys = SystemMessage(content=system_prompt)
    user = HumanMessage(
        content=(
            f"질의:\n{q}\n\n"
            f"아웃라인(참고):\n{outline_block}\n\n"
            f"컨텍스트 샘플:\n" + "\n".join(ctx_snippets)
        )
    )
    answer_text = ""
    try:
        resp = llm.invoke([sys, user])
        answer_text = (getattr(resp, "content", None) or "").strip()
    except Exception:
        # Fallback deterministic skeleton
        answer_text = f"요약 답변:\n- {q}\n\n근거는 제공된 문서에 기반합니다."

    # Append sources section
    sources_section = _render_sources_section(sources, label=label) if add_section else ""
    final_text = answer_text
    if sources_section:
        final_text = f"{answer_text}\n\n{sources_section}"

    log = (state.get("log") or []) + [{"at": "generate_answer", "ts": _now()}]
    out = {
        "answer": final_text,
        "phase": "final",
        "log": log,
    }
    return out

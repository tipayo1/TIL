# nodes.py (FeatureTree + ε-greedy + VersionStore + metrics++ + preprocess/type-guard)

import os
import time
import random

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
    epsilon_best_strategy,
)

from policy import EPSILON


# Shared DataFlowManager & thread pool (IO-bound tasks)
_DFM = DataFlowManager()
_EXEC = ThreadPoolExecutor(max_workers=int(os.getenv("RAG_MAX_WORKERS", "4")))
_STORE = RPGVersionStore(root_dir=os.getenv("RPG_STORE_DIR"))

# ---------------- Preprocess & type guards ----------------
def _dfm_fill_defaults(frm: str, to: str, st: Dict[str, Any]) -> Dict[str, Any]:
    out = dict(st or {})
    out.setdefault("retrieval_hints", {"k": 8, "strategy": "semantic"})
    out.setdefault("plugins", [])
    out.setdefault("log", [])
    out.setdefault("documents", [])
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
        content = None
        role = None
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
            ok = ext in [".py", ".ipynb", ".md", ".rst", ".json", ".yaml", ".yml", ".toml"]
        elif ctx == "conversational":
            ok = ext in [".md", ".txt", ".html", ".htm"]
        if ok:
            kept.append(d)
    return kept

def _thread_id(state: State) -> str:
    return (state.get("thread_id") or os.getenv("THREAD_ID") or "default")

# ---------------- Compose RPG ----------------
def compose_rpg(state: State) -> Dict[str, Any]:
    q = (_get_question(state) or state.get("refined_query") or state.get("query") or "").strip()
    context_type = _infer_context_type(q)

    # Build context RPG and registry
    rpg_graph = configure_rag_for_context(context_type, q)
    registry_obj = RAGComponentRegistry()
    registry = registry_obj.to_dict()

    # base hints + registry binding
    hints = state.get("retrieval_hints") or {"k": 8, "strategy": "semantic"}
    hints = bind_registry_to_hints(registry, context_type, hints)  # merge feature->module/file hints
    hints = registry_obj.merge_feature_hints(hints)  # feature tree: minimal derivation from hints

    ft_roots = [
        FeatureTreeNode(fid="retrieval", name="Retrieval", children=[
            FeatureTreeNode(fid="retrieval.semantic", name="Semantic", score=0.5, file_hint="retrievers/semantic.py"),
            FeatureTreeNode(fid="retrieval.hybrid", name="Hybrid", score=0.6, file_hint="retrievers/hybrid.py"),
            FeatureTreeNode(fid="retrieval.expand", name="Expand", score=0.7, file_hint="retrievers/expand.py"),
        ]),
        FeatureTreeNode(fid="rerank", name="Rerank", children=[
            FeatureTreeNode(fid="rerank.cross_encoder", name="CrossEncoder", score=0.7, file_hint="rerankers/cross_encoder.py"),
            FeatureTreeNode(fid="rerank.llm_based", name="LLM", score=0.5, file_hint="rerankers/llm_based.py"),
        ]),
    ]

    ft = FeatureTree(ft_roots)
    selected = epsilon_best_strategy(ft, epsilon=EPSILON)
    # Persist lightweight selection/version info if store is configured
    try:
        if _STORE is not None:
            _STORE.save({"ts": _now(), "ctx": context_type, "feature": selected})
    except Exception:
        pass

    log = (state.get("log") or []) + [{"at": "compose_rpg", "ctx": context_type, "selected": selected, "ts": _now()}]
    out = {
        "query": q or state.get("query"),
        "refined_query": q,
        "context_type": context_type,
        "rpg_graph": rpg_graph,
        "registry": registry,
        "retrieval_hints": hints,
        "feature_choice": selected,
        "log": log,
    }
    out["flow_violations"] = _append_flow_violations(state, "compose_rpg", "intent_parser", out)
    return out

# ---------------- Intent parse ----------------
def intent_parser(state: State) -> Dict[str, Any]:
    q = _get_question(state)
    # Simple heuristic refining
    refined = q.strip()
    log = (state.get("log") or []) + [{"at": "intent_parser", "refined": refined, "ts": _now()}]
    out = dict(state or {})
    out.update({"refined_query": refined, "log": log})
    out["flow_violations"] = _append_flow_violations(state, "intent_parser", "retrieve_rpg", out)
    return out

# ---------------- Retrieval ----------------
def retrieve_rpg(state: State) -> Dict[str, Any]:
    vs = get_vectorstore()
    q = state.get("refined_query") or state.get("query") or ""
    hints = (state.get("retrieval_hints") or {}).copy()
    k = int(hints.get("k", 8))
    strategy = hints.get("strategy", "semantic")
    meta_filter = hints.get("filter")

    seen = set()
    pairs: List[Tuple[Document, float]] = []

    # Basic semantic search
    pairs.extend(_run_vs_search(vs, q, k, meta_filter))

    # Optional hybrid addition (simple heuristic)
    if strategy == "hybrid":
        # lightweight simulate by increasing k and merging
        more = _run_vs_search(vs, q, max(1, k // 2), meta_filter)
        pairs.extend(more)

    docs = _merge_scored_docs(pairs, seen)
    # Context-aware filter using RPG subgraph
    docs = _apply_rpg_subgraph_filter(docs, state)

    prev_docs = state.get("documents") or []
    metrics = _calc_metrics(docs, k, q, prev_docs)

    log = (state.get("log") or []) + [{"at": "retrieve_rpg", "n": len(docs), "k": k, "strategy": strategy, "ts": _now()}]
    out = dict(state or {})
    out.update({
        "documents": docs,
        "retrieval_metrics": metrics,
        "last_retrieval_ts": _now(),
        "log": log,
    })
    out["flow_violations"] = _append_flow_violations(state, "retrieve_rpg", "award_xp", out)
    return out

# ---------------- Expand search ----------------
def expand_search(state: State) -> Dict[str, Any]:
    vs = get_vectorstore()
    q = state.get("refined_query") or state.get("query") or ""
    hints = (state.get("retrieval_hints") or {}).copy()
    base_k = int(hints.get("k", 8))
    new_k = min(32, base_k * 2)
    meta_filter = hints.get("filter")

    seen = set((d.page_content.strip()[:120], (d.metadata or {}).get("source", "")) for d in (state.get("documents") or []))
    pairs = _run_vs_search(vs, q, new_k, meta_filter)
    more_docs = _merge_scored_docs(pairs, seen)

    docs = (state.get("documents") or []) + more_docs
    metrics = _calc_metrics(docs, new_k, q, state.get("documents") or [])

    log = (state.get("log") or []) + [{"at": "expand_search", "added": len(more_docs), "k": new_k, "ts": _now()}]
    out = dict(state or {})
    out.update({
        "documents": docs,
        "retrieval_metrics": metrics,
        "retrieval_hints": {**hints, "k": new_k, "strategy": "expand"},
        "log": log,
    })
    out["flow_violations"] = _append_flow_violations(state, "expand_search", "rerank", out)
    return out

# ---------------- Award XP ----------------
def award_xp(state: State) -> Dict[str, Any]:
    m = state.get("retrieval_metrics") or {}
    # Simple XP heuristic: coverage and diversity weighted
    xp = round(100 * (0.5 * float(m.get("coverage", 0)) + 0.5 * float(m.get("diversity", 0))), 2)
    log = (state.get("log") or []) + [{"at": "award_xp", "xp": xp, "metrics": m, "ts": _now()}]
    out = dict(state or {})
    out.update({"xp": xp, "log": log})
    # Next hop decided by policy.decide_after_xp in the graph
    return out

# ---------------- Rerank ----------------
def rerank(state: State) -> Dict[str, Any]:
    docs = state.get("documents") or []
    # Default rerank by existing score desc; placeholder for CE/LLM rerank
    reranked = sorted(docs, key=lambda d: float((d.metadata or {}).get("score") or 0.0), reverse=True)
    log = (state.get("log") or []) + [{"at": "rerank", "n": len(reranked), "ts": _now()}]
    out = dict(state or {})
    out.update({"documents": reranked, "log": log})
    out["flow_violations"] = _append_flow_violations(state, "rerank", "plan_answer", out)
    return out

# ---------------- Plan answer ----------------
def plan_answer(state: State) -> Dict[str, Any]:
    q = state.get("refined_query") or state.get("query") or ""
    docs = state.get("documents") or []

    # Build lightweight plan: select top sources and key points
    top = docs[: min(5, len(docs))]
    sources = []
    for d in top:
        md = d.metadata or {}
        sources.append(md.get("source") or md.get("url") or "unknown")

    plan = {
        "steps": [
            {"id": 1, "action": "summarize", "detail": "Top documents summary"},
            {"id": 2, "action": "ground", "detail": "Ground answer with citations"},
            {"id": 3, "action": "finalize", "detail": "Produce concise answer"},
        ],
        "sources": sources,
        "k": len(top),
    }
    log = (state.get("log") or []) + [{"at": "plan_answer", "k": plan["k"], "ts": _now()}]
    out = dict(state or {})
    out.update({"answer_plan": plan, "log": log})
    out["flow_violations"] = _append_flow_violations(state, "plan_answer", "generate_answer", out)
    return out

# ---------------- Generate answer ----------------
def generate_answer(state: State) -> Dict[str, Any]:
    llm = get_llm()
    q = state.get("refined_query") or state.get("query") or ""
    docs = state.get("documents") or []
    plan = state.get("answer_plan") or {}

    context_blurb = "\n\n".join(
        f"- [{(d.metadata or {}).get('source') or (d.metadata or {}).get('url') or 'unknown'}] {d.page_content[:300]}"
        for d in docs[: min(5, len(docs))]
    )
    sys = SystemMessage(content="You are a helpful assistant. Ground answers in provided context when possible.")
    hum = HumanMessage(content=f"Question: {q}\n\nContext:\n{context_blurb}\n\nPlan: {plan}")

    resp = llm.invoke([sys, hum])
    text = getattr(resp, "content", None) or getattr(resp, "text", None) or str(resp)

    messages = (state.get("messages") or []) + [{"role": "assistant", "content": text}]
    log = (state.get("log") or []) + [{"at": "generate_answer", "len": len(text or ''), "ts": _now()}]
    out = dict(state or {})
    out.update({"answer": text, "messages": messages, "log": log})
    return out

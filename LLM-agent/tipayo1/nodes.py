# nodes.py (RPG versioning + subgraph filter + concurrency-safe search)

import os
import time
from dotenv import load_dotenv

load_dotenv()

from typing import List, Dict, Optional, Any, Tuple, Callable
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
)

# Shared DataFlowManager & thread pool (IO-bound tasks)
_DFM = DataFlowManager()
_EXEC = ThreadPoolExecutor(max_workers=int(os.getenv("RAG_MAX_WORKERS", "4")))

# ---------------- Utilities ----------------
def _append_flow_violations(state: State, frm: str, to: str, snapshot: Dict[str, Any]) -> List[Dict[str, Any]]:
    res = _DFM.validate(frm, to, snapshot)
    violations = (state.get("flow_violations") or [])[:]
    if not res.get("ok"):
        for v in res.get("violations", []):
            violations.append({"from": frm, "to": to, "error": v})
    return violations

def _get_question(state: State) -> str:
    # prefer latest human/user message; fallback to explicit field
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

def _calc_metrics(docs: List[Document], k: int) -> Dict[str, Any]:
    n = len(docs)
    scores = [
        float((d.metadata or {}).get("score") or 0.0)
        for d in docs
        if isinstance((d.metadata or {}).get("score"), (int, float))
    ]
    avg_score = round(sum(scores) / len(scores), 4) if scores else 0.0
    coverage = round(min(1.0, n / max(1, k)), 3)
    diversity = _source_diversity(docs)
    return {"k": k, "n": n, "avg_score": avg_score, "coverage": coverage, "diversity": diversity}

def _run_vs_search(vs, q: str, k: int, meta_filter: Optional[Dict[str, Any]] = None) -> List[Tuple[Document, float]]:
    # execute similarity search in thread pool to avoid blocking event loops
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

# ---------- RPG persistence helpers ----------
def _now() -> float:
    return time.time()

def _merge_rpg_graph(prev: Dict[str, Any], new: Dict[str, Any]) -> Dict[str, Any]:
    # Minimal, conservative merge: prefer new meta, keep both roots; deduplicate by name
    prev_roots = {r.get("name"): r for r in (prev.get("roots") or []) if isinstance(r, dict)}
    new_roots = {r.get("name"): r for r in (new.get("roots") or []) if isinstance(r, dict)}
    merged_names = list({*prev_roots.keys(), *new_roots.keys()})
    roots = []
    for name in merged_names:
        # new overrides on name collision
        roots.append(new_roots.get(name) or prev_roots.get(name))
    meta = dict(prev.get("meta") or {})
    meta.update(new.get("meta") or {})
    return {"meta": meta, "roots": roots}

def _update_rpg_versions(state: State, new_graph_dict: Dict[str, Any], note: str) -> Dict[str, Any]:
    versions = list(state.get("rpg_versions") or [])
    curr_version = int(state.get("rpg_version") or 0)
    prev_graph = (state.get("rpg") or {}).get("graph")

    if prev_graph:
        merged = _merge_rpg_graph(prev_graph, new_graph_dict)
    else:
        merged = new_graph_dict

    # append snapshot of previous as versioned history (keep tail N)
    N = int(os.getenv("RPG_VERSION_HISTORY", "10"))
    if prev_graph:
        versions.append({"version": curr_version, "graph": prev_graph, "ts": _now(), "note": "prev"})
        if len(versions) > N:
            versions = versions[-N:]

    return {
        "rpg": {"graph": merged, "registry": (state.get("rpg") or {}).get("registry") or {}, "flows": (state.get("rpg") or {}).get("flows") or []},
        "rpg_versions": versions,
        "rpg_version": curr_version + 1,
        "log": (state.get("log") or []) + [{"phase": "setup", "rpg_version": curr_version + 1, "note": note}],
    }

# ---------- Subgraph filter ----------
def _doc_context_ok(doc: Document, ctx: str, q_terms: List[str]) -> bool:
    md = doc.metadata or {}
    ext = (md.get("ext") or "").lower()
    ns_terms = md.get("ns_terms") or []

    if ctx == "legal":
        # If section terms are present in query, require overlap; else allow legal-friendly formats
        if q_terms:
            return any(t in ns_terms for t in q_terms)
        return ext in [".pdf", ".docx", ".md", ".txt"]
    if ctx == "technical":
        return ext in [".py", ".ipynb", ".md", ".rst", ".json", ".yaml", ".yml", ".toml"]
    if ctx == "conversational":
        return ext in [".md", ".txt", ".html", ".htm"]
    return True

def _apply_rpg_subgraph_filter(docs: List[Document], state: State) -> List[Document]:
    ctx = state.get("context_type") or "general"
    q = state.get("refined_query") or state.get("query") or ""
    q_terms = extract_section_terms(q) or []
    kept: List[Document] = []
    for d in docs:
        if _doc_context_ok(d, ctx, q_terms):
            kept.append(d)
    return kept

# ---------------- Compose RPG ----------------
def compose_rpg(state: State) -> Dict[str, Any]:
    q = (_get_question(state) or state.get("refined_query") or state.get("query") or "").strip()
    context_type = _infer_context_type(q)

    # Build fresh RPG by context
    rpg_graph = configure_rag_for_context(context_type, q)
    registry = RAGComponentRegistry().to_dict()

    # base hints + registry binding
    hints = state.get("retrieval_hints") or {"k": 8, "strategy": "semantic"}
    hints = bind_registry_to_hints(registry, context_type, hints)

    # optional plugins
    plugins = state.get("plugins") or []
    if context_type == "legal":
        p = LegalRetrievalPlugin()
        upd = p.execute({"retrieval_hints": hints, "plugins": plugins})
        hints = upd.get("retrieval_hints", hints)
        plugins = upd.get("plugins", plugins)

    flows = _DFM.describe()
    path = rpg_graph.suggest_execution_path(state.get("retrieval_metrics") or {})
    schema_issues = unit_test_flow_assertions(_DFM)

    # RPG versioning: merge with previous + record history
    base_update = {
        "execution_path": path,
        "retrieval_hints": hints,
        "context_type": context_type,
        "plugins": plugins,
        "phase": "setup",
        "flow_violations": state.get("flow_violations") or [],
    }
    # Ensure registry/flows are available for new 'rpg'
    state_prime = {**state, **{"rpg": {"graph": (state.get("rpg") or {}).get("graph"), "registry": registry, "flows": flows}}}
    vupd = _update_rpg_versions(state_prime, rpg_graph.to_dict(), note="compose")

    log = (vupd.get("log") or []) + [{"phase": "setup", "rpg": True, "path": path, "schema_issues": schema_issues}]
    return {
        **base_update,
        **vupd,
        "log": log,
    }

# ---------------- Intent parsing ----------------
def intent_parser(state: State) -> Dict[str, Any]:
    base = _get_question(state)
    prev_q = (state.get("query") or "").strip()
    reset_block: Dict[str, Any] = {}
    if base and base != prev_q:
        reset_block = {
            "retrieved_docs": [],
            "retrieval_metrics": {},
            "answer_plan": [],
            "answer": "",
        }

    hints = state.get("retrieval_hints") or {"k": 8, "strategy": "semantic"}
    update: Dict[str, Any] = {
        "query": base,
        "refined_query": base,
        "retrieval_hints": hints,
        "phase": "refine",
        **reset_block,
    }

    violations = _append_flow_violations(state, "intent_parser", "retrieve_rpg", {**state, **update})
    log = (state.get("log") or []) + [{"phase": "refine", "refined_query": base, "hints": hints, "violations": len(violations)}]
    update["log"] = log
    update["flow_violations"] = violations
    return update

# ---------------- Primary retrieval ----------------
def retrieve_rpg(state: State) -> Dict[str, Any]:
    vs = get_vectorstore()
    q = state.get("refined_query") or state.get("query") or ""
    hints = state.get("retrieval_hints") or {}
    k = int(hints.get("k") or 8)
    strategy = hints.get("strategy", "semantic")
    section_boost = bool(hints.get("section_boost"))

    # Build an optional metadata filter from RPG if available (kept minimal here)
    meta_filter: Optional[Dict[str, Any]] = None

    docs: List[Document] = []
    if strategy == "hybrid":
        # run two searches concurrently and merge
        terms = extract_section_terms(q) or []
        expanded_query = (q + " " + " ".join(terms)).strip() if terms else q
        fut_a = _EXEC.submit(vs.similarity_search_with_score, q, int(k * 0.6), None, meta_filter)
        fut_b = _EXEC.submit(vs.similarity_search_with_score, expanded_query, int(k * 0.6), None, meta_filter)
        pairs = fut_a.result() + fut_b.result()
        seen = set()
        docs = _merge_scored_docs(pairs, seen)
    else:
        # semantic but with legal section boost if requested
        base_pairs = _run_vs_search(vs, q, k, meta_filter)
        seen = set()
        docs = _merge_scored_docs(base_pairs, seen)
        if section_boost:
            terms = extract_section_terms(q) or []
            if terms:
                expanded_query = (q + " " + " ".join(terms)).strip()
                extra_pairs = _run_vs_search(vs, expanded_query, max(4, int(k * 0.5)), meta_filter)
                docs += _merge_scored_docs(extra_pairs, seen)

    # RPG subgraph filter BEFORE prompt injection
    docs = _apply_rpg_subgraph_filter(docs, state)

    metrics = _calc_metrics(docs, k)
    update = {"retrieved_docs": docs, "retrieval_metrics": metrics, "phase": "search"}
    violations = _append_flow_violations(state, "retrieve_rpg", "award_xp", {**state, **update})
    log = (state.get("log") or []) + [{"phase": "search", "k": k, "strategy": strategy, "metrics": metrics, "violations": len(violations)}]
    update["log"] = log
    update["flow_violations"] = violations
    return update

# ---------------- Expanded retrieval ----------------
def expand_search(state: State) -> Dict[str, Any]:
    vs = get_vectorstore()
    q = state.get("refined_query") or state.get("query") or ""
    terms = extract_section_terms(q) or []
    expanded = (q + " " + " ".join(terms)).strip() if terms else q

    base_docs = state.get("retrieved_docs") or []
    k = int((state.get("retrieval_hints") or {}).get("k", 16))

    meta_filter: Optional[Dict[str, Any]] = None
    pairs = _run_vs_search(vs, expanded, k, meta_filter)

    seen = set((d.page_content.strip()[:120], (d.metadata or {}).get("source", "")) for d in base_docs)
    new_docs = _merge_scored_docs(pairs, seen)

    merged = list(base_docs) + new_docs
    # Apply subgraph filter again to expanded set to avoid drift
    merged = _apply_rpg_subgraph_filter(merged, state)

    metrics = _calc_metrics(merged, k)
    update = {"retrieved_docs": merged, "retrieval_metrics": metrics, "phase": "expand"}
    violations = _append_flow_violations(state, "expand_search", "rerank", {**state, **update})
    log = (state.get("log") or []) + [{"phase": "expand", "query": expanded, "metrics": metrics, "violations": len(violations)}]
    update["log"] = log
    update["flow_violations"] = violations
    return update

# ---------------- XP update and path refresh ----------------
def award_xp(state: State) -> Dict[str, Any]:
    met = state.get("retrieval_metrics") or {}
    xp = int(state.get("xp") or 0)
    fails = int(state.get("fail_count") or 0)
    n = int(met.get("n") or 0)
    coverage = float(met.get("coverage") or 0.0)
    diversity = float(met.get("diversity") or 0.0)
    delta = 1 + int(coverage * 3) + int(diversity * 2) + (2 if n >= 8 else 0)
    xp += max(1, delta)
    if n == 0:
        fails += 1

    try:
        from rpg import RPGGraph  # local import
        new_path = RPGGraph().suggest_execution_path(met)
    except Exception:
        new_path = state.get("execution_path") or []

    # Keep current merged RPG and bump version note=award_xp (no graph change)
    vupd = _update_rpg_versions(state, (state.get("rpg") or {}).get("graph") or {"meta": {}, "roots": []}, note="award_xp")

    update = {
        "xp": xp,
        "fail_count": fails,
        "execution_path": new_path or state.get("execution_path") or [],
        "phase": state.get("phase") or "search",
        **vupd,
    }

    # logging only (branching is handled by graph conditional edges)
    log = (state.get("log") or []) + [{"phase": "search", "xp_award": delta, "xp_total": xp, "path": new_path}]
    update["log"] = log
    update["flow_violations"] = state.get("flow_violations") or []
    return update

# ---------------- Rerank ----------------
def rerank(state: State) -> Dict[str, Any]:
    docs = state.get("retrieved_docs") or []
    docs = sorted(docs, key=lambda d: float((d.metadata or {}).get("score") or 0.0), reverse=True)[:20]
    update = {"retrieved_docs": docs, "phase": "rerank"}
    violations = _append_flow_violations(state, "rerank", "plan_answer", {**state, **update})
    log = (state.get("log") or []) + [{"phase": "rerank", "kept": len(docs), "violations": len(violations)}]
    update["log"] = log
    update["flow_violations"] = violations
    return update

# ---------------- Plan ----------------
def plan_answer(state: State) -> Dict[str, Any]:
    docs = state.get("retrieved_docs") or []
    q = state.get("refined_query") or state.get("query") or ""
    plan: List[Dict[str, Any]] = []
    for i, d in enumerate(docs[:8]):
        snippet = d.page_content.strip().splitlines()[0][:160]
        plan.append({"claim": f"근거 {i+1}: {snippet}", "evidence": [i]})
    update = {"answer_plan": plan, "phase": "plan"}
    violations = _append_flow_violations(state, "plan_answer", "generate_answer", {**state, **update})
    log = (state.get("log") or []) + [{"phase": "plan", "items": len(plan), "query": q, "violations": len(violations)}]
    update["log"] = log
    update["flow_violations"] = violations
    return update

# ---------------- Generate ----------------
def generate_answer(state: State) -> Dict[str, Any]:
    llm = get_llm()
    q = state.get("refined_query") or state.get("query") or ""
    docs = state.get("retrieved_docs") or []
    plan = state.get("answer_plan") or []
    evid_texts: List[str] = []
    for item in plan[:6]:
        for idx in item.get("evidence", []):
            if 0 <= idx < len(docs):
                d = docs[idx]
                src = (d.metadata or {}).get("source") or ""
                evid_texts.append(f"[{idx}] {src}: {d.page_content[:300]}")
    system = SystemMessage(content="답변은 근거 기반으로 간결하게 작성하고, 필요한 경우 근거 색인 번호를 각 문단 끝에 대괄호로 표기하세요.")
    human = HumanMessage(content=f"질문: {q}\n\n근거 후보:\n" + "\n".join(evid_texts))
    resp = llm.invoke([system, human])
    text = getattr(resp, "content", "") if hasattr(resp, "content") else str(resp)
    log = (state.get("log") or []) + [{"phase": "answer", "chars": len(text)}]
    return {"answer": text, "phase": "answer", "log": log}

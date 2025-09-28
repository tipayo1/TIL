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
    # citation policy defaults (plug-and-play via env)
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

# ---------------- Compose RPG ----------------
def compose_rpg(state: State) -> Dict[str, Any]:
    q = (_get_question(state) or state.get("refined_query") or state.get("query") or "").strip()
    context_type = _infer_context_type(q)

    # Build context RPG and registry
    rpg_graph = configure_rag_for_context(context_type, q)
    registry_obj = RAGComponentRegistry()
    registry = registry_obj.to_dict()

    # Bind hints by context and optional plugin
    hints = bind_registry_to_hints(registry, context_type, base_hints=state.get("retrieval_hints") or {})
    plugins = list(state.get("plugins") or [])
    if context_type == "legal":
        leg = LegalRetrievalPlugin()
        plug_out = leg.execute({"retrieval_hints": hints, "plugins": plugins})
        hints = plug_out.get("retrieval_hints", hints)
        plugins = plug_out.get("plugins", plugins)

    # Execution path suggestion
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
    }
    snap = _DFM.preprocess("compose_rpg", "intent_parser", {**(state or {}), **out})
    out["flow_violations"] = _append_flow_violations(state, "compose_rpg", "intent_parser", snap)
    return out

# ---------------- Intent parsing ----------------
def intent_parser(state: State) -> Dict[str, Any]:
    q = (_get_question(state) or state.get("query") or "").strip()
    refined = q  # 최소 정제
    hints = dict(state.get("retrieval_hints") or {})
    out = {"refined_query": refined, "retrieval_hints": hints, "phase": "refine"}
    snap = _DFM.preprocess("intent_parser", "retrieve_rpg", {**(state or {}), **out})
    out["flow_violations"] = _append_flow_violations(state, "intent_parser", "retrieve_rpg", snap)
    return out

# ---------------- Retrieval ----------------
def retrieve_rpg(state: State) -> Dict[str, Any]:
    q = state.get("refined_query") or state.get("query") or ""
    hints = dict(state.get("retrieval_hints") or {})
    k = int(hints.get("k", 8))
    meta_filter: Dict[str, Any] = {}
    if hints.get("section_boost"):
        meta_filter["ext"] = {"$in": [".pdf", ".docx", ".md", ".txt"]}

    vs = get_vectorstore(auto_bootstrap=True)
    pairs = _run_vs_search(vs, q, k, meta_filter or None)

    seen = set()
    docs = _merge_scored_docs(pairs, seen)
    docs = _apply_rpg_subgraph_filter(docs, state)

    metrics = _calc_metrics(docs, k, q, prev_docs=None)
    log = (state.get("log") or []) + [{"at": "retrieve_rpg", "n": len(docs), "ts": _now()}]
    out = {"documents": docs, "retrieval_metrics": metrics, "phase": "search", "log": log}
    snap = _DFM.preprocess("retrieve_rpg", "award_xp", {**(state or {}), **out})
    out["flow_violations"] = _append_flow_violations(state, "retrieve_rpg", "award_xp", snap)
    return out

# ---------------- Expand search ----------------
def expand_search(state: State) -> Dict[str, Any]:
    q = state.get("refined_query") or state.get("query") or ""
    hints = dict(state.get("retrieval_hints") or {})
    base_k = int(hints.get("k", 8))
    k = max(base_k, int(base_k * 2))

    vs = get_vectorstore(auto_bootstrap=False)  # 이미 올라온 인덱스 사용
    pairs = _run_vs_search(vs, q, k, None)

    seen = set(((d.page_content.strip()[:120], (d.metadata or {}).get("source", "")) for d in state.get("documents") or []))
    new_docs = _merge_scored_docs(pairs, seen)
    docs = (state.get("documents") or []) + new_docs

    metrics = _calc_metrics(docs, k, q, prev_docs=state.get("documents") or [])
    log = (state.get("log") or []) + [{"at": "expand_search", "n": len(new_docs), "ts": _now()}]
    out = {"documents": docs, "retrieval_metrics": metrics, "phase": "expand", "log": log}
    snap = _DFM.preprocess("expand_search", "rerank", {**(state or {}), **out})
    out["flow_violations"] = _append_flow_violations(state, "expand_search", "rerank", snap)
    return out

# ---------------- Award XP ----------------
def award_xp(state: State) -> Dict[str, Any]:
    met = state.get("retrieval_metrics") or {}
    xp_inc = int(5 * max(0.0, min(1.0, met.get("coverage", 0.0))) + 3 * max(0.0, 1.0 - met.get("negative_rate", 1.0)))
    xp = int(state.get("xp") or 0) + xp_inc
    log = (state.get("log") or []) + [{"at": "award_xp", "xp_inc": xp_inc, "ts": _now()}]
    out = {"xp": xp, "log": log}
    return out

# ---------------- Rerank (stub) ----------------
def rerank(state: State) -> Dict[str, Any]:
    # 최소 스텁: 문서 유지, 메트릭 재계산 가능
    q = state.get("refined_query") or state.get("query") or ""
    docs = state.get("documents") or []
    k = int((state.get("retrieval_hints") or {}).get("k", max(8, len(docs))))
    metrics = _calc_metrics(docs, k, q, prev_docs=None)
    log = (state.get("log") or []) + [{"at": "rerank", "ts": _now()}]
    out = {"documents": docs, "retrieval_metrics": metrics, "phase": "rerank", "log": log}
    snap = _DFM.preprocess("rerank", "plan_answer", {**(state or {}), **out})
    out["flow_violations"] = _append_flow_violations(state, "rerank", "plan_answer", snap)
    return out

# ---------------- Plan answer ----------------
def plan_answer(state: State) -> Dict[str, Any]:
    docs = state.get("documents") or []
    plan = []
    for i, d in enumerate(docs[:5]):
        plan.append({
            "claim": f"evidence_{i+1}",
            "evidence": [i],
            "source": (d.metadata or {}).get("source") or (d.metadata or {}).get("url") or "unknown",
        })
    log = (state.get("log") or []) + [{"at": "plan_answer", "items": len(plan), "ts": _now()}]
    out = {"answer_plan": plan, "phase": "plan", "log": log}
    snap = _DFM.preprocess("plan_answer", "generate_answer", {**(state or {}), **out})
    out["flow_violations"] = _append_flow_violations(state, "plan_answer", "generate_answer", snap)
    return out

# ---------------- Generate answer (Perplexity-style citations) ----------------
def generate_answer(state: State) -> Dict[str, Any]:
    llm = get_llm()
    q = state.get("refined_query") or state.get("query") or ""
    docs = state.get("documents") or []
    plan = state.get("answer_plan") or []
    policy = dict(state.get("citation_policy") or {})
    enable = bool(policy.get("enable", True))
    max_n = int(policy.get("max", 8))
    label = str(policy.get("label", "출처"))
    append_section = bool(policy.get("append_section", True))

    # Build compact context and sources
    context_blurb = "\n\n".join(
        f"- [{(d.metadata or {}).get('source') or (d.metadata or {}).get('url') or 'unknown'}] {d.page_content[:300]}"
        for d in docs[: min(5, len(docs))]
    )
    sources = _unique_sources(docs, limit=max_n)

    # Messages with explicit inline-citation instruction
    if enable:
        sys_text = (
            "You are a helpful assistant. Use the provided context and the numbered SOURCES.\n"
            "Cite claims inline with bracketed numbers like [1], [2] that refer to the SOURCES list.\n"
            "If a claim is not supported, say so briefly."
        )
        hum_text = (
            f"Question: {q}\n\n"
            f"Context:\n{context_blurb}\n\n"
            "SOURCES:\n" + "\n".join(f"[{i+1}] {s}" for i, s in enumerate(sources)) + "\n\n"
            f"Plan: {plan}\n\n"
            "Instruction: Include inline citations [n] mapped to SOURCES and end with a Sources section mirroring the numbering."
        )
    else:
        sys_text = "You are a helpful assistant. Ground answers in provided context when possible."
        hum_text = f"Question: {q}\n\nContext:\n{context_blurb}\n\nPlan: {plan}"

    sys = SystemMessage(content=sys_text)
    hum = HumanMessage(content=hum_text)

    resp = llm.invoke([sys, hum])
    text = getattr(resp, "content", None) or getattr(resp, "text", None) or str(resp)

    # Failsafe: append Sources section if missing
    if enable and append_section:
        lower = (text or "").lower()
        if ("sources" not in lower) and (label not in (text or "")):
            section = _render_sources_section(sources, label=label)
            if section:
                text = f"{text}\n\n{section}"

    messages = (state.get("messages") or []) + [{"role": "assistant", "content": text}]
    log = (state.get("log") or []) + [{"at": "generate_answer", "len": len(text or ''), "sources": len(sources), "ts": _now()}]

    out = dict(state or {})
    out.update({
        "answer": text,
        "sources": sources,
        "citation_policy": policy,
        "messages": messages,
        "log": log,
        "phase": "answer",
    })
    return out

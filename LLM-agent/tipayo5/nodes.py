# nodes.py (경량 LEGO 블록: compose → intent → retrieve → award_xp → expand|rerank → plan → generate)

import os
import time
import json
import hashlib
from typing import List, Dict, Optional, Any, Tuple

from langchain_core.documents import Document
from langchain_core.messages import HumanMessage, SystemMessage

from state import State
from db import get_vectorstore, get_llm
from rpg import (
    configure_rag_for_context,
    bind_registry_to_hints,
    get_prompt,
    call_tool,
    suggest_tools_for_context,
)

# ---------------- Env / constants ----------------

_FT_ALPHA = float(os.getenv("RPG_FT_ALPHA", "0.3"))
_MAX_EXPANDS = int(os.getenv("RPG_MAX_EXPANDS", "3"))
_USE_UNIT_TEST = os.getenv("RPG_USE_UNIT_TESTS", "0") not in ("0", "false", "False")
_AB_POLICY = os.getenv("RPG_AB_POLICY", "A")
_CE_MODEL = os.getenv("RERANK_CE_MODEL", "").strip()

# ---------------- Helpers ----------------

def _moving_avg(old: Optional[float], new: float, alpha: float = _FT_ALPHA) -> float:
    if old is None:
        return new
    return alpha * new + (1.0 - alpha) * float(old)

def _hash_dict(obj: Dict[str, Any]) -> str:
    norm = json.dumps(obj, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(norm).hexdigest()

def _trim_log(log: Optional[List[Dict[str, Any]]], max_len: int = 200) -> List[Dict[str, Any]]:
    return (log or [])[-max_len:]

def _apply_meta_filter_by_context(ctx: str) -> Optional[Dict[str, Any]]:
    if ctx == "technical":
        return {"ext": {"$in": [".py", ".ipynb", ".md", ".rst", ".json", ".yaml", ".yml", ".toml"]}}
    if ctx == "legal":
        return {"ext": {"$in": [".pdf", ".docx", ".txt", ".md"]}}
    return None

def _run_vs_search(vs, query: str, k: int = 8, meta_filter: Optional[Dict[str, Any]] = None) -> List[Tuple[Document, float]]:
    try:
        if meta_filter:
            docs = vs.similarity_search_with_score(query, k=k, filter=meta_filter)
        else:
            docs = vs.similarity_search_with_score(query, k=k)
    except Exception:
        docs = vs.similarity_search_with_score(query, k=k)
    return docs

def _unique_by_source_scored(pairs: List[Tuple[Document, float]], top_k: int = 12) -> List[Tuple[Document, float]]:
    seen = set()
    out: List[Tuple[Document, float]] = []
    for d, s in pairs:
        src = (d.metadata or {}).get("source") or (d.metadata or {}).get("id") or d.page_content[:50]
        if src in seen:
            continue
        seen.add(src)
        out.append((d, s))
        if len(out) >= top_k:
            break
    return out

def _boost_with_ns_terms(pairs: List[Tuple[Document, float]], boost: float = 0.03) -> List[Tuple[Document, float]]:
    """문서 메타의 ns_terms 개수 기반 경량 부스팅."""
    out: List[Tuple[Document, float]] = []
    for d, s in pairs:
        terms = (d.metadata or {}).get("ns_terms") or []
        inc = len([t for t in terms if t])
        out.append((d, s + boost * inc))
    out.sort(key=lambda x: x[1], reverse=True)
    return out

def _metrics_from_pairs(pairs: List[Tuple[Document, float]], k: int) -> Dict[str, Any]:
    n = len(pairs)
    avg = sum(s for _, s in pairs) / max(n, 1)
    sources = {(d.metadata or {}).get("source", "") for d, _ in pairs}
    diversity = len(sources) / max(n, 1)
    coverage = n / max(k, 1)
    negative_rate = sum(1 for _, s in pairs if s <= 0) / max(n, 1)
    return {
        "k": k,
        "n": n,
        "avg_score": avg,
        "coverage": coverage,
        "diversity": diversity,
        "intent_coverage": 0.0,
        "negative_rate": negative_rate,
        "novel_evidence_contrib": 0.0,
    }

def _token_overlap(a: str, b: str) -> float:
    at = set((a or "").lower().split())
    bt = set((b or "").lower().split())
    if not at or not bt:
        return 0.0
    inter = len(at & bt)
    norm = (len(at) ** 0.5) * (len(bt) ** 0.5)
    return inter / max(1.0, norm)

def _apply_rerank(pairs: List[Tuple[Document, float]], query: str, strategy: Optional[str]) -> List[Tuple[Document, float]]:
    """
    경량 리랭커:
    - strategy가 비어있으면 원 순서 유지
    - cross_encoder/llm_based일 때 토큰 중첩 점수로 재정렬
    """
    strat = (strategy or "none").lower()
    if strat == "none":
        return pairs
    scored: List[Tuple[Document, float]] = []
    for d, _ in pairs:
        score = _token_overlap(query, d.page_content or "")
        scored.append((d, score))
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored

def _guess_context(q: str) -> str:
    ql = (q or "").lower()
    if any(t in q for t in ["법", "조문", "판례", "헌법", "소송", "법률"]):
        return "legal"
    if any(t in ql for t in ["stack trace", "exception", "traceback", "def ", "class ", "python", "에러", "오류"]):
        return "technical"
    if any(t in q for t in ["안녕", "고마워", "말해줘", "대화", "상담"]):
        return "conversational"
    return "general"

def _choose_template_key(query: str, context_type: str) -> str:
    ql = (query or "").lower()
    if any(k in ql for k in ["요약", "summar"]):
        return "summarize"
    return "qa_grounded"

# ---------------- Nodes ----------------

def compose_rpg(state: State) -> Dict[str, Any]:
    t0 = time.time()
    q = state.get("query") or ""
    context_type = state.get("context_type") or _guess_context(q)

    reg, tpl, onto = configure_rag_for_context(context_type)

    base_hints: Dict[str, Any] = {"k": 8, "must_terms": []}
    hints = bind_registry_to_hints(reg.to_dict(), context_type, base_hints)
    hints = onto.enrich(q, hints)

    # 컨텍스트별 기본 툴 제안 추가
    hints["tools"] = suggest_tools_for_context(context_type)

    subtree_choice = {"retrieval": hints.get("strategy", "hybrid")}

    # minimal RPG graph/meta
    rpg_graph = {"meta": {"context": context_type}, "roots": []}
    rpg = {"graph": rpg_graph, "registry": reg.to_dict(), "flows": ["compose", "intent", "retrieve", "rerank", "generate"]}

    # versioning
    vnum = int(state.get("rpg_version") or 0) + 1
    versions = list(state.get("rpg_versions") or [])
    versions.append({"version": vnum, "graph": rpg_graph, "ts": time.time(), "note": "auto"})

    log = (state.get("log") or []) + [{"phase": "setup", "dt": time.time() - t0, "note": f"ctx={context_type}, strat={hints.get('strategy')}"}]
    log = _trim_log(log)

    return {
        "context_type": context_type,
        "rpg": rpg,
        "rpg_version": vnum,
        "rpg_versions": versions,
        "retrieval_hints": hints,
        "template_hints": {"domain": context_type},
        "ontology_version": str(hints.get("ontology_version", "")),
        "subtree_choice": subtree_choice,
        "phase": "setup",
        "execution_path": (state.get("execution_path") or []) + ["compose_rpg"],
        "log": log,
    }

def intent_parser(state: State) -> Dict[str, Any]:
    t0 = time.time()
    q = state.get("query") or ""
    refined = " ".join(q.split()).strip()
    log = (state.get("log") or []) + [{"phase": "refine", "dt": time.time() - t0, "note": "normalize"}]
    log = _trim_log(log)
    return {
        "refined_query": refined or q,
        "phase": "refine",
        "execution_path": (state.get("execution_path") or []) + ["intent_parser"],
        "log": log,
    }

def retrieve_rpg(state: State) -> Dict[str, Any]:
    t0 = time.time()
    q = state.get("refined_query") or state.get("query") or ""
    hints = dict(state.get("retrieval_hints") or {})
    k = int(hints.get("k") or 8)
    ctx = state.get("context_type") or "general"
    meta_filter = _apply_meta_filter_by_context(ctx)

    vs = get_vectorstore()
    pairs = _run_vs_search(vs, q, k=k, meta_filter=meta_filter)
    pairs = _unique_by_source_scored(pairs, top_k=max(k, 12))
    pairs = _boost_with_ns_terms(pairs, boost=0.03)

    docs = [d for d, _ in pairs]
    metrics = _metrics_from_pairs(pairs, k=k)

    log = (state.get("log") or []) + [{"phase": "search", "dt": time.time() - t0, "note": f"k={k}, n={len(docs)}"}]
    log = _trim_log(log)

    # initialize expands counter
    hints.setdefault("expands", 0)

    return {
        "retrieved_docs": docs,
        "retrieval_metrics": metrics,
        "retrieval_hints": hints,
        "phase": "search",
        "execution_path": (state.get("execution_path") or []) + ["retrieve_rpg"],
        "log": log,
    }

def award_xp(state: State) -> Dict[str, Any]:
    t0 = time.time()
    metrics = dict(state.get("retrieval_metrics") or {})
    gain = int(10.0 * float(metrics.get("coverage") or 0.0) + 10.0 * float(metrics.get("diversity") or 0.0))
    xp = int(state.get("xp") or 0) + gain
    xp_total = float(state.get("xp_total") or 0.0) + float(gain)

    log = (state.get("log") or []) + [{"phase": "search", "dt": time.time() - t0, "note": f"xp+={gain}"}]
    log = _trim_log(log)

    return {
        "xp": xp,
        "xp_total": xp_total,
        "phase": "search",
        "execution_path": (state.get("execution_path") or []) + ["award_xp"],
        "log": log,
    }

def expand_search(state: State) -> Dict[str, Any]:
    t0 = time.time()
    q = state.get("refined_query") or state.get("query") or ""
    hints = dict(state.get("retrieval_hints") or {})
    ctx = state.get("context_type") or "general"
    meta_filter = _apply_meta_filter_by_context(ctx)

    expands = int(hints.get("expands") or 0) + 1
    hints["expands"] = expands

    base_k = int(hints.get("k") or 8)
    new_k = min(base_k + 4 * expands, 32)
    hints["k"] = new_k

    must_terms = " ".join(hints.get("must_terms") or [])
    aug_q = f"{q} {must_terms}".strip()

    vs = get_vectorstore()
    pairs = _run_vs_search(vs, aug_q, k=new_k, meta_filter=meta_filter)
    pairs = _unique_by_source_scored(pairs, top_k=max(new_k, 12))
    pairs = _boost_with_ns_terms(pairs, boost=0.03)

    docs = [d for d, _ in pairs]
    metrics = _metrics_from_pairs(pairs, k=new_k)

    log = (state.get("log") or []) + [{"phase": "expand", "dt": time.time() - t0, "note": f"k={new_k}, n={len(docs)}"}]
    log = _trim_log(log)

    return {
        "retrieval_hints": hints,
        "retrieved_docs": docs,
        "retrieval_metrics": metrics,
        "phase": "expand",
        "execution_path": (state.get("execution_path") or []) + ["expand_search"],
        "log": log,
    }

def rerank(state: State) -> Dict[str, Any]:
    t0 = time.time()
    q = state.get("refined_query") or state.get("query") or ""
    hints = dict(state.get("retrieval_hints") or {})
    strategy = hints.get("reranker") or "none"

    docs = list(state.get("retrieved_docs") or [])
    pairs = [(d, float(len(d.page_content or ""))) for d in docs]  # initial weak score
    pairs = _apply_rerank(pairs, q, strategy=strategy)

    # keep top-N
    top_k = min(12, len(pairs))
    pairs = pairs[:top_k]
    docs_out = [d for d, _ in pairs]

    # loopback decision: if empty and can expand more
    expands = int(hints.get("expands") or 0)
    if not docs_out and expands < _MAX_EXPANDS:
        phase = "expand"
        note = "need_more_evidence"
    else:
        phase = "rerank"
        note = f"top={len(docs_out)}"

    log = (state.get("log") or []) + [{"phase": "rerank", "dt": time.time() - t0, "note": note}]
    log = _trim_log(log)

    return {
        "retrieved_docs": docs_out,
        "phase": phase,  # graph checks for "expand" to loop; otherwise continues
        "execution_path": (state.get("execution_path") or []) + ["rerank"],
        "log": log,
    }

def plan_answer(state: State) -> Dict[str, Any]:
    t0 = time.time()
    docs: List[Document] = list(state.get("retrieved_docs") or [])

    # 간단 계획: 상위 문서에서 스니펫 추출
    top_n = min(5, len(docs))
    plan: List[Dict[str, Any]] = []
    sources: List[str] = []
    for idx in range(top_n):
        d = docs[idx]
        src = (d.metadata or {}).get("source") or (d.metadata or {}).get("id") or f"doc_{idx+1}"
        if src not in sources:
            sources.append(src)
        content = (d.page_content or "").strip().splitlines()
        snippet = "\n".join(content[:3])[:600]
        plan.append({"claim": f"evidence_{idx+1}", "snippet": snippet, "source": src})

    citation_policy = {
        "enable": True,
        "max": 5,
        "inline": False,
        "append_section": True,
        "label": "출처",
    }

    log = (state.get("log") or []) + [{"phase": "plan", "dt": time.time() - t0, "note": f"plan k={len(plan)}"}]
    log = _trim_log(log)

    return {
        "answer_plan": plan,
        "sources": sources,
        "citation_policy": citation_policy,
        "phase": "plan",
        "execution_path": (state.get("execution_path") or []) + ["plan_answer"],
        "log": log,
    }

def generate_answer(state: State) -> Dict[str, Any]:
    t0 = time.time()
    q = state.get("refined_query") or state.get("query") or ""
    plan: List[Dict[str, Any]] = state.get("answer_plan") or []
    sources: List[str] = state.get("sources") or []
    policy = state.get("citation_policy") or {"enable": True, "append_section": True, "label": "출처"}
    hints = dict(state.get("retrieval_hints") or {})
    ctx = state.get("context_type") or "general"

    # 프롬프트 레지스트리 기반 메시지
    evidence_lines = []
    for i, p in enumerate(plan, start=1):
        snippet = p.get("snippet", "")
        src = p.get("source", f"doc_{i}")
        evidence_lines.append(f"[{i}] ({src})\n{snippet}")
    template_key = _choose_template_key(q, ctx)
    prompt_vars = {"query": q, "context": "\n\n".join(evidence_lines)}
    pr = get_prompt(template_key, prompt_vars)

    sys = SystemMessage(content=pr["system"])
    hm = HumanMessage(content=pr["user"])

    llm = get_llm(temperature=0.2)
    try:
        answer_core = llm.invoke([sys, hm]).content.strip()
    except Exception:
        answer_core = "증거가 충분하지 않아 확답을 제공하기 어렵다."

    # 간단한 출처 섹션
    if policy.get("enable") and policy.get("append_section"):
        label = policy.get("label", "출처")
        uniq_sources = []
        for s in sources:
            if s and s not in uniq_sources:
                uniq_sources.append(s)
        if uniq_sources:
            answer_core = f"{answer_core}\n\n{label}:\n" + "\n".join(f"- {s}" for s in uniq_sources)

    # 선택적 툴 호출 (예: citation_check)
    tool_calls: List[Dict[str, Any]] = []
    for tool_name in (hints.get("tools") or []):
        try:
            result = call_tool(tool_name, {"answer": answer_core, "docs": [{"text": p.get("snippet", "")} for p in plan]}, {"context_type": ctx})
            tool_calls.append({"name": tool_name, "result": result})
        except Exception as e:
            tool_calls.append({"name": tool_name, "error": str(e)})

    # 간단한 검증 결과 주석 추가
    for c in tool_calls:
        if c.get("name") == "citation_check" and isinstance(c.get("result"), dict):
            if not c["result"].get("ok"):
                answer_core = f"{answer_core}\n\n[검증 메모] 인용 표시가 부족할 수 있습니다."

    log = (state.get("log") or []) + [{"phase": "answer", "dt": time.time() - t0, "note": "generated", "tools": tool_calls}]
    log = _trim_log(log)

    return {
        "answer": answer_core,
        "final_answer": answer_core,
        "answer_type": "rag_answer",
        "phase": "end",
        "execution_path": (state.get("execution_path") or []) + ["generate_answer"],
        "log": log,
    }

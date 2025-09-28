# nodes.py
# - LEGO 블록 노드: compose → intent → retrieve → award_xp → expand|rerank → plan → generate
# - 각 노드는 단일 책임, 분기는 policy에서만 수행
# - execution_path 누적으로 Studio 단계 가시성 확보
# - 노드 시그니처: (state, config[RunnableConfig]) 선택 도입

import os
from typing import List, Dict, Optional, Any, Tuple

from langchain_core.documents import Document
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.runnables import RunnableConfig

from state import State
from db import get_vectorstore, get_llm, simple_overlap_score
from rpg import (
    RAGComponentRegistry,
    TemplateRegistry,
    OntologyProvider,
    bind_registry_to_hints,
    get_prompt,
)
from policy import need_expand, decide_after_xp

# ---------------- Env / constants ----------------
_MAX_EXPANDS = int(os.getenv("RPG_MAX_EXPANDS", "3"))

# Optional Sentry hook
_SENTRY_DSN = os.getenv("SENTRY_DSN", "").strip()
if _SENTRY_DSN:
    try:
        import sentry_sdk  # type: ignore
        sentry_sdk.init(dsn=_SENTRY_DSN)
    except Exception:
        pass

# ---------------- 공통 데코레이터 ----------------
def trace_node(node_name: str):
    """
    - phase 설정, execution_path 누적, 노드 예외 로깅
    - LangGraph 권장 config 인자 패턴 지원(state, config)
    - 운영시 Sentry 훅을 통해 예외 보고 가능(옵션)
    - Command 반환 패턴도 가능하나, 본 구현은 조건부 엣지로 라우팅(그래프에서 관리)
    """
    def wrapper(fn):
        def inner(state: State, config: Optional[RunnableConfig] = None) -> State:
            state["phase"] = node_name
            ep = list(state.get("execution_path", []))
            ep.append(node_name)
            state["execution_path"] = ep
            try:
                if config is None:
                    return fn(state)
                # 함수가 config를 받지 않는 경우 안전 폴백
                try:
                    return fn(state, config)
                except TypeError:
                    return fn(state)
            except Exception as e:
                log = list(state.get("log", []))
                log.append({"node": node_name, "error": str(e)})
                state["log"] = log
                state["fail_count"] = int(state.get("fail_count", 0)) + 1
                if _SENTRY_DSN:
                    try:
                        import sentry_sdk  # type: ignore
                        sentry_sdk.capture_exception(e)
                    except Exception:
                        pass
                raise
        return inner
    return wrapper

# ---------------- Helpers ----------------
def _doc_id(doc: Document) -> str:
    mid = (doc.metadata or {}).get("id")
    if mid:
        return str(mid)
    return str(abs(hash((doc.page_content or "")[:200])))

def _compute_metrics(query: str, docs: List[Document], must_terms: List[str], filters: Dict[str, Any]) -> Dict[str, Any]:
    """
    경량 메트릭 집계(coverage/diversity/intent_coverage/negative_rate/ontology_coverage)
    """
    if not docs:
        return {
            "k": 0, "n": 0, "avg_score": 0.0, "coverage": 0.0, "diversity": 0.0,
            "intent_coverage": 0.0, "negative_rate": 1.0, "novel_evidence_contrib": 0.0,
            "ontology_coverage": 0.0
        }

    scores = [simple_overlap_score(query, d) for d in docs]
    avg = sum(scores) / len(scores) if scores else 0.0
    sources = [str((d.metadata or {}).get("source", "unknown")) for d in docs]
    uniq = len(set(sources)) / float(max(1, len(sources)))
    neg = sum(1 for d in docs if not (d.page_content or "").strip()) / float(len(docs))

    def _match(d: Document) -> float:
        text = (d.page_content or "").lower()
        must_ok = all((t or "").lower() in text for t in (must_terms or [])) if must_terms else True
        filt_ok = True
        md = d.metadata or {}
        for k, v in (filters or {}).items():
            if isinstance(v, (list, tuple, set)):
                if md.get(k) not in v:
                    filt_ok = False
                    break
            else:
                if md.get(k) != v:
                    filt_ok = False
                    break
        return 1.0 if (must_ok and filt_ok) else 0.0

    onto_cov = sum(_match(d) for d in docs) / float(len(docs))
    return {
        "k": len(docs),
        "n": len(docs),
        "avg_score": avg,
        "coverage": avg,
        "diversity": uniq,
        "intent_coverage": max(0.0, min(1.0, avg + 0.05)),
        "negative_rate": neg,
        "novel_evidence_contrib": 0.0,
        "ontology_coverage": onto_cov,
    }

# ---------------- Nodes ----------------

@trace_node("compose_rpg")
def compose_rpg(state: State, config: Optional[RunnableConfig] = None) -> State:
    """
    - 레지스트리/템플릿/온톨로지 초기화
    - 온톨로지 분석 → 기본 hints 생성 → 레지스트리 병합
    - RPG 메타 스냅샷 저장
    """
    reg = RAGComponentRegistry()
    templ = TemplateRegistry()
    onto = OntologyProvider()
    q = state.get("query", "") or ""
    onto_hints = onto.analyze(q)

    hints = {
        "must_terms": onto_hints.get("must_terms", []),
        "filters": onto_hints.get("filters", {}),
        "strategy": "hybrid",
        # rerank 기본은 overlap, 필요 시 환경으로 경량 CE 활성화
        "rerank": "overlap" if not os.getenv("RERANK_CE_ENABLE", "").strip() else "lite_ce",
    }
    hints = bind_registry_to_hints(reg, hints)

    state["retrieval_hints"] = hints
    state["template_hints"] = {"style": "concise"}
    state["ontology_version"] = onto_hints.get("ontology_version", "v0.1-lite")
    state["ontology_entities"] = {"entities": onto_hints.get("entities", []), "domain": onto_hints.get("domain", "general")}
    state["rpg"] = {"version": "rpg-lite-0.2", "registry": reg.snapshot(), "flows": []}

    # 학습/진행/메타 초기화
    state["xp"] = int(state.get("xp", 0))
    state["xp_total"] = float(state.get("xp_total", 0.0))
    state["fail_count"] = int(state.get("fail_count", 0))
    state["log"] = list(state.get("log", []))
    state["execution_path"] = list(state.get("execution_path", []))
    state["seen_doc_ids"] = list(state.get("seen_doc_ids", []))
    state["feature_tree_lite"] = state.get("feature_tree_lite", {"routing": {"prefer": "rerank"}})

    # config 활용 예시(표준화): thread_id를 로그에 남김
    tid = ((config or {}).get("configurable") or {}).get("thread_id") if config else None
    if tid:
        state["log"].append({"node": "compose_rpg", "thread_id": tid})

    return state

@trace_node("intent_parser")
def intent_parser(state: State, config: Optional[RunnableConfig] = None) -> State:
    """
    - LLM으로 retrieval 친화적 질의 정제
    - 템플릿 기반 System/Human 메시지 구성
    """
    templ = TemplateRegistry()
    llm = get_llm(temperature=0.0)
    sys = SystemMessage(content=get_prompt(templ, "system_base"))
    hm = HumanMessage(content=f"{get_prompt(templ, 'ask_intent')}\n\nQuery:\n{state.get('query','')}")
    out = llm.invoke([sys, hm])
    refined = out.content.strip() if hasattr(out, "content") else state.get("query", "")
    state["refined_query"] = refined
    return state

@trace_node("retrieve_rpg")
def retrieve_rpg(state: State, config: Optional[RunnableConfig] = None) -> State:
    """
    - VectorStore에서 k개 검색 (전략/파라미터는 hints에서)
    - 메타데이터/온톨로지 must_terms 필터를 적용
    - 경량 메트릭 계산 및 저장
    """
    hints = state.get("retrieval_hints", {}) or {}
    params = hints.get("params", {}) or {}
    k = int(params.get("k", 8))
    filters = hints.get("filters", {}) or {}
    must_terms = hints.get("must_terms", []) or []

    vs = get_vectorstore()
    query = state.get("refined_query") or state.get("query") or ""
    fetch_k = int(params.get("fetch_k", max(k * 3, k + 10)))  # FAISS 폴백 대비
    pairs: List[Tuple[Document, float]] = vs.similarity_search_with_score(
        query, k=k, filters=filters, must_terms=must_terms, fetch_k=fetch_k  # type: ignore
    )

    docs = [p[0] for p in pairs] if pairs else []
    metrics = _compute_metrics(query, docs, must_terms, filters)

    state["retrieved_docs"] = docs
    state["retrieval_metrics"] = metrics
    return state

@trace_node("award_xp")
def award_xp(state: State, config: Optional[RunnableConfig] = None) -> State:
    """
    - 새 증거 공헌도: 이전에 보지 않은 문서 비율을 novel로 반영
    - xp/xp_total 갱신
    """
    seen = set(state.get("seen_doc_ids", []))
    docs = state.get("retrieved_docs", []) or []
    new_ids = []
    for d in docs:
        did = _doc_id(d)
        if did not in seen:
            new_ids.append(did)
            seen.add(did)

    novel_rate = (len(new_ids) / float(max(1, len(docs)))) if docs else 0.0
    metrics = dict(state.get("retrieval_metrics", {}) or {})
    metrics["novel_evidence_contrib"] = novel_rate
    state["retrieval_metrics"] = metrics

    inc = 1.0 if novel_rate >= 0.3 else 0.5 if novel_rate > 0 else 0.2
    state["xp"] = int(state.get("xp", 0)) + 1
    state["xp_total"] = float(state.get("xp_total", 0.0)) + inc
    state["seen_doc_ids"] = list(seen)
    return state

@trace_node("expand_search")
def expand_search(state: State, config: Optional[RunnableConfig] = None) -> State:
    """
    - 힌트만 갱신(폭 확장): k 증가, diversity 옵션 부여 등
    - 실제 재검색은 그래프 엣지 루프로 retrieve_rpg에서 수행
    """
    hints = dict(state.get("retrieval_hints", {}) or {})
    params = dict(hints.get("params", {}) or {})
    params["k"] = int(params.get("k", 8)) + 4  # 점진 확장
    params["diversity_boost"] = True
    params["fetch_k"] = max(int(params.get("fetch_k", 0)), params["k"] * 3)
    hints["params"] = params
    state["retrieval_hints"] = hints

    # 확장 횟수 추적(로그)
    meta = dict(state.get("rpg", {}) or {})
    flows = list(meta.get("flows", []))
    flows.append({"at": "expand_search", "k": params["k"]})
    meta["flows"] = flows
    state["rpg"] = meta
    return state

@trace_node("rerank")
def rerank(state: State, config: Optional[RunnableConfig] = None) -> State:
    """
    - 선택적 경량 CE 리랭크, 기본은 overlap 폴백
    - 문서 순서를 정제하고 상위 k만 유지
    """
    hints = state.get("retrieval_hints", {}) or {}
    docs = list(state.get("retrieved_docs", []) or [])
    query = state.get("refined_query") or state.get("query") or ""
    params = hints.get("params", {}) or {}
    k = int(params.get("k", 8))
    if not docs:
        return state

    rerank_params = hints.get("rerank_params", {}) or {}
    rtype = rerank_params.get("type", "overlap")
    ranked: List[Tuple[Document, float]]

    if rtype == "cross_encoder":
        model_name = rerank_params.get("model") or os.getenv("RERANK_CE_MODEL", "").strip()
        if model_name:
            try:
                from sentence_transformers import CrossEncoder  # type: ignore
                bs = int(rerank_params.get("batch_size", int(os.getenv("RERANK_CE_BATCH_SIZE", "16"))))
                topn = int(rerank_params.get("topn", int(os.getenv("RERANK_TOPN", str(k)))))
                cand = docs[:max(k, min(len(docs), topn))]
                pairs = [[query, d.page_content or ""] for d in cand]
                ce = CrossEncoder(model_name)
                scores = ce.predict(pairs, batch_size=bs)
                ranked = sorted(list(zip(cand, [float(s) for s in scores])), key=lambda x: x[1], reverse=True)
                state["retrieved_docs"] = [d for d, _ in ranked[:k]]
                return state
            except Exception:
                # 폴백: overlap
                pass

    # 기본/폴백: overlap
    ranked = sorted([(d, simple_overlap_score(query, d)) for d in docs], key=lambda x: x[1], reverse=True)
    state["retrieved_docs"] = [d for d, _ in ranked[:k]]
    return state

@trace_node("plan_answer")
def plan_answer(state: State, config: Optional[RunnableConfig] = None) -> State:
    """
    - LLM으로 다중 클레임 계획 간단 생성
    - 증거 인덱스는 상위 3개 문서를 매핑(간이)
    """
    templ = TemplateRegistry()
    llm = get_llm(temperature=0.0)
    sys = SystemMessage(content=get_prompt(templ, "system_base"))
    joined = "\n\n".join([f"[{i}] {d.page_content[:400]}" for i, d in enumerate(state.get("retrieved_docs", [])[:3])])
    hm = HumanMessage(content=f"{get_prompt(templ, 'plan_answer')}\n\nQuery:\n{state.get('refined_query') or state.get('query','')}\n\nEvidence:\n{joined}")
    out = llm.invoke([sys, hm])
    plan_text = out.content.strip() if hasattr(out, "content") else ""
    claims = [ln.strip("- ").strip() for ln in plan_text.splitlines() if ln.strip()]
    plan = [{"claim": c, "evidence": [0, 1, 2]} for c in claims[:3]] or [{"claim": "Direct answer", "evidence": [0, 1]}]
    state["answer_plan"] = plan
    return state

@trace_node("generate_answer")
def generate_answer(state: State, config: Optional[RunnableConfig] = None) -> State:
    """
    - LLM으로 최종 생성
    - citation_policy에 따라 출처 라벨 포함
    """
    templ = TemplateRegistry()
    llm = get_llm(temperature=0.2)
    sys = SystemMessage(content=get_prompt(templ, "system_base"))
    ev = state.get("retrieved_docs", []) or []
    joined = "\n\n".join([f"[{i}] {d.page_content[:600]}" for i, d in enumerate(ev[:5])])
    hm = HumanMessage(content=f"{get_prompt(templ, 'generate_answer')}\n\nPlan:\n{state.get('answer_plan')}\n\nEvidence:\n{joined}\n\nQuery:\n{state.get('refined_query') or state.get('query','')}")
    out = llm.invoke([sys, hm])
    answer = out.content.strip() if hasattr(out, "content") else ""
    state["answer"] = answer

    # 출처 수집(중복 제거)
    srcs: List[str] = []
    for d in ev[:5]:
        src = str((d.metadata or {}).get("source", "")) or "doc"
        if src not in srcs:
            srcs.append(src)
    state["sources"] = srcs
    return state

# 참고: 특정 노드에서 “업데이트 + 라우팅”을 동시 처리해야 할 케이스는
# Command 반환 패턴으로 대체 가능(예: return Command(goto="rerank")),
# 본 설계는 정책 외부화 + 조건부 엣지로 라우팅을 유지(그래프에서 관리).

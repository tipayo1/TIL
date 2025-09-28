# nodes.py

from dotenv import load_dotenv
load_dotenv()

import json
from typing import Dict, List, Tuple, Optional, TypedDict, Literal, cast, Any

from langchain_core.documents import Document
from langchain_core.messages import AIMessage

from state import State
from utils import get_llm, extract_query_terms_llm, compute_retrieval_metrics
from scripts.create_pinecone_index import get_vectorstore

# =============================================
# 공통 도우미
# =============================================
def _append_path(state: State, node: str) -> List[str]:
    path = list(state.get("execution_path") or [])
    path.append(node)
    return path

def _get_question(state: State) -> str:
    q = (state.get("user_question") or "").strip()
    if q:
        return q
    msgs = state.get("messages") or []
    for m in reversed(list(msgs)):
        content = None
        role = None
        if hasattr(m, "content"):
            content = getattr(m, "content", None)
            role = getattr(m, "type", None) or getattr(m, "role", None)
        if isinstance(m, dict):
            content = m.get("content", content)
            role = m.get("type") or m.get("role") or role
        if isinstance(content, str) and content.strip():
            if role in (None, "human", "user"):
                return content.strip()
    return ""

# =============================================
# Node: 사용자 질문 정제
# =============================================
def refine_question(state: State) -> dict:
    _llm = get_llm("gen")
    question = _get_question(state)
    prompt = f"""
당신은 "정보통신기획평가원(IITP)" 기관내부규정 챗봇의 전처리 노드입니다.
사용자의 질문을 정제해 주세요.

규칙:
1) 한국어 유지, 불필요 특수문자 제거, 공백 정리
2) HR 용어 표준화 (반차/대체휴가/복지 포인트 등)
3) 한국어 없이 전부 영어면 "invalid_input"

사용자 질문:
{question}

위 규칙으로 불필요한 내용은 제거하고 출력하라.
""".strip()
    result = _llm.invoke(prompt).content.strip() if question else ""
    return {
        "user_question": question,
        "refined_question": result,
        "execution_path": _append_path(state, "refine_question"),
    }

# =============================================
# Node: RPG 제안(계획) 합성
# =============================================
class RPGPlan(TypedDict, total=False):
    query: str
    strategies: Dict[str, Any]  # {"retrieval":{"k":int}, "rerank":{...}, "generator":{...}}
    terms: List[str]

def compose_rpg(state: State) -> dict:
    """질문→쿼리/용어/전략(k) 경량 RPG 계획 생성"""
    q = state.get("refined_question") or _get_question(state) or ""
    terms = extract_query_terms_llm(q)
    # 간결한 기본 전략 (LLM 가이드라인 포함)
    plan: RPGPlan = {
        "query": q,
        "terms": terms,
        "strategies": {
            "retrieval": {"k": int((len(terms) // 3) + 3)},  # 3~5 기본
            "rerank": {"mode": "llm-score", "top_k": 3},
            "generator": {"style": "concise", "cite": True},
        },
    }
    return {
        "rpg_plan": plan,
        "execution_path": _append_path(state, "compose_rpg"),
        "xp": int(state.get("xp", 0)),
    }

# =============================================
# Node: 리트리버 (RPG 계획 적용)
# =============================================
def retrieve(state: State) -> dict:
    vs = get_vectorstore(index_name="IITP-rules")
    plan = state.get("rpg_plan") or {}
    refined_question = (plan.get("query") or state.get("refined_question") or _get_question(state) or "").strip()
    if not refined_question:
        return {"retrieved_docs": [], "execution_path": _append_path(state, "retrieve")}

    # k는 계획 우선, 폴백 3
    k = int(((plan.get("strategies") or {}).get("retrieval") or {}).get("k", 3))
    # terms가 있으면 보강 질의
    terms = plan.get("terms") or []
    if terms:
        refined_question = f"{refined_question} | 키워드: " + ", ".join(terms)

    retriever = vs.as_retriever(search_kwargs={"k": k})
    docs = retriever.invoke(refined_question)
    return {
        "retrieved_docs": docs,
        "execution_path": _append_path(state, "retrieve"),
    }

# =============================================
# Node: 재순위화(LLM 점수)
# =============================================
def rerank(state: State) -> dict:
    llm = get_llm("reranker")
    question = _get_question(state)
    docs_in = state.get("retrieved_docs") or []
    if not question or not docs_in:
        return {
            "retrieved_docs": docs_in,
            "execution_path": _append_path(state, "rerank"),
        }

    import re
    scored: List[Tuple[Document, float]] = []
    for doc in docs_in:
        prompt = f"""
질문: "{question}"
문서 내용: "{doc.page_content}"
0~1 사이 숫자로 관련도만 출력:
""".strip()
        txt = (llm.invoke(prompt).content or "").strip()
        cleaned = txt.replace(",", ".")
        m = re.search(r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?", cleaned)
        try:
            score = float(m.group()) if m else 0.0
        except Exception:
            score = 0.0
        score = max(0.0, min(1.0, score))
        scored.append((doc, score))
    scored.sort(key=lambda x: x[1], reverse=True)

    plan = state.get("rpg_plan") or {}
    top_k = int(((plan.get("strategies") or {}).get("rerank") or {}).get("top_k", 3))
    top_docs = [doc for doc, _ in scored[:top_k]]

    return {
        "retrieved_docs": top_docs,
        "execution_path": _append_path(state, "rerank"),
    }

# =============================================
# Node: 메트릭 산출 및 XP 부여
# =============================================
def award_xp(state: State) -> dict:
    plan = state.get("rpg_plan") or {}
    terms = plan.get("terms") or extract_query_terms_llm(state.get("refined_question") or "")
    docs = state.get("retrieved_docs") or []
    met = compute_retrieval_metrics(terms, docs)

    # 계획의 k 반영
    k_planned = int(((plan.get("strategies") or {}).get("retrieval") or {}).get("k", len(docs) or 1))
    met["k"] = k_planned

    return {
        "retrieval_metrics": met,
        "execution_path": _append_path(state, "award_xp"),
    }

# =============================================
# Node: 확장 검색 (LLM 용어 확장 + k 증분)
# =============================================
def expand_search(state: State) -> dict:
    plan = dict(state.get("rpg_plan") or {})
    strategies = dict((plan.get("strategies") or {}))
    retr = dict((strategies.get("retrieval") or {}))

    # k 증분 (선형 확장)
    k_curr = int(retr.get("k", 3))
    k_next = k_curr + 2
    retr["k"] = k_next

    # 용어 확장
    base_q = plan.get("query") or state.get("refined_question") or _get_question(state) or ""
    new_terms = extract_query_terms_llm(base_q)
    old_terms = plan.get("terms") or []
    merged_terms = list(dict.fromkeys((old_terms or []) + (new_terms or [])))[:10]

    plan["terms"] = merged_terms
    strategies["retrieval"] = retr
    plan["strategies"] = strategies

    return {
        "rpg_plan": plan,
        "xp": int(state.get("xp", 0)) + 1,
        "execution_path": _append_path(state, "expand_search"),
    }

# =========================
# Answer_type: Rag_answer
# =========================
def generate_rag_answer(state: State) -> dict:
    _llm = get_llm("gen")
    question = _get_question(state)
    if not question:
        return {
            "final_answer": "문서에 근거가 없어 답변드리기 어렵습니다. 다시 질문해주세요.",
            "execution_path": _append_path(state, "generate_rag_answer"),
        }

    context = ""
    for i, doc in enumerate(state.get("retrieved_docs", []), start=1):
        context += f"[{i}] ({doc.metadata.get('source', 'unknown')})\n{doc.page_content}\n\n"
    if not context.strip():
        return {
            "final_answer": "문서에 근거가 없어 답변드리기 어렵습니다. 관련 출처가 검색되지 않았습니다.",
            "execution_path": _append_path(state, "generate_rag_answer"),
        }

    prompt = f"""
당신은 "정보통신기획평가원(IITP)"의 기관내부규정 안내 챗봇입니다.
아래 출처 문서 내용만을 근거로 질문에 대해 명확하고 간결하게 답변하세요.
문서에 명시된 내용이 없으면 "문서에 근거가 없어 답변드리기 어렵습니다."라고 답하세요.
인용한 문장 끝에는 [출처 번호]를 붙이고, 마지막에 '출처 목록'을 정리하세요.

# 질문
{question}

# 출처 문서
{context}

# 답변
""".strip()
    answer = _llm.invoke(prompt).content.strip()
    return {
        "messages": [AIMessage(content=answer)],
        "final_answer": answer,
        "execution_path": _append_path(state, "generate_rag_answer"),
    }

# =============================================
# Node: RAG 답변 검증
# =============================================
def verify_rag_answer(state: State) -> dict:
    _llm = get_llm("judge")
    context = ""
    for doc in state.get("retrieved_docs", []):
        context += f"- {doc.page_content}\n"
    final_answer = state.get("final_answer", "")

    if not context.strip() or not final_answer.strip():
        return {"verification": "불일치함", "execution_path": _append_path(state, "verify_rag_answer")}

    prompt = f"""
생성 답변이 문서 내용에만 근거했는지 검증하라.
완전히 일치하면 '일치함', 조금이라도 다르면 '불일치함'만 출력하라.

# 문서
{context}

# 답변
"{final_answer}"

# 판단 (일치함/불일치함):
""".strip()
    verdict = (_llm.invoke(prompt).content or "").strip()
    final_verdict = "일치함" if "일치함" in verdict else "불일치함"
    return {"verification": final_verdict, "execution_path": _append_path(state, "verify_rag_answer")}

# =============================================
# Node: HR 여부 판별
# =============================================
class HRAnalysis(TypedDict):
    is_hr_question: bool

DEPARTMENTS = {
    "재무": {"name": "재무", "email": "fi@gaida.play.com", "slack": "#ask-fi"},
    "총무": {"name": "총무", "email": "ga@gaida.play.com", "slack": "#ask-ga"},
    "인프라": {"name": "인프라", "email": "in@gaida.play.com", "slack": "#ask-in"},
    "보안": {"name": "보안", "email": "se@gaida.play.com", "slack": "#ask-se"},
    "인사": {"name": "인사", "email": "hr@gaida.play.com", "slack": "#ask-hr"},
}

def update_hr_status(state: State) -> State:
    """HR 여부만 판별, 그 결과를 상태에 저장"""
    prompt = f"""
당신은 "정보통신기획평가원(IITP)"의 기관내부규정 안내 챗봇입니다.
원본/정제 질문을 보고 HR 관련 여부만 JSON으로 응답하세요.

원본: "{state.get('user_question','')}"
정제: "{state.get('refined_question','')}"

형식:
{{"is_hr_question": true}} 또는 {{"is_hr_question": false}}
""".strip()
    _llm = get_llm("router1")
    structured_llm = _llm.with_structured_output(HRAnalysis)
    result: HRAnalysis = structured_llm.invoke(prompt)
    is_hr = bool(result.get("is_hr_question", False))
    answer_type = "pending" if is_hr else "reject"
    out = {**state, "is_hr_question": is_hr, "answer_type": answer_type, "execution_path": _append_path(state, "update_hr_status")}
    return cast(State, out)

# =========================
# Answer_type: Reject
# =========================
def generate_reject_answer(state: State):
    reject_answer = "입력하신 질문은 IITP의 기관내부규정 관련 문의가 아닙니다. IITP의 기관내부규정 관련 질문만 가능합니다."
    return {
        "messages": [AIMessage(content=reject_answer)],
        "final_answer": reject_answer,
        "execution_path": _append_path(state, "generate_reject_answer"),
    }

# =============================================
# Node: RAG 여부 판별
# =============================================
class RAGDepartmentAnalysis(TypedDict, total=False):
    route: str            # "rag" 또는 "department"
    department: str       # department인 경우에만

def _classify_rag_or_department(question: str) -> Dict[str, str]:
    """LLM 통합 분류: RAG vs 담당자 + 부서"""
    system_prompt = f"""
정제된 질문을 보고 처리 방식을 결정하라.

정제된 질문: "{question}"

[route 기준]
- rag: 문서에서 일반 규정을 찾을 수 있는 정보성 질문
- department: 개인 맞춤/승인/신고/민감 사안 등

[부서 키워드]
- 재무: 세금, 예산, 회계, 지출, 송금, 계산서, 청구서, 지급, 비용, 환급
- 총무: 사무실, 비품, 물품, 구매, 수령, 우편, 시설, 행사, 차량, 청소, 자산, 출장, 숙박, 교통
- 인프라: 서버, 네트워크, 컴퓨터, IT, 소프트웨어, 장비, 시스템, 접속, VPN, 계정, 접근
- 보안: 보안, 해킹, 정보, 유출, 침해, 랜섬웨어, 백신, 데이터, 비밀번호, 방화벽, 악성코드, 암호
- 인사: 개별 급여/채용/평가/퇴직/상담

응답(JSON):
rag인 경우: {{"route":"rag"}}
담당자인 경우: {{"route":"department","department":"부서명"}}
부득이하면 인사로 지정.
""".strip()
    _llm = get_llm("router2")
    structured_llm = _llm.with_structured_output(RAGDepartmentAnalysis)
    try:
        result: RAGDepartmentAnalysis = structured_llm.invoke(system_prompt)
        return result
    except Exception:
        return {"route": "department", "department": "인사"}

def update_rag_status(state: State) -> State:
    """LLM 기반 질문 분류 및 라우팅 상태 업데이트"""
    question = state.get('refined_question') or _get_question(state) or ""
    classification_result = _classify_rag_or_department(question)
    route = classification_result.get("route")
    department_name = classification_result.get("department")

    if route == "rag":
        out = {**state, "is_rag_suitable": True, "department_info": None, "answer_type": "rag_answer"}
    else:
        department_info = DEPARTMENTS.get(department_name or "", DEPARTMENTS["인사"])
        out = {**state, "is_rag_suitable": False, "department_info": department_info, "answer_type": "department_contact"}
    out["execution_path"] = _append_path(state, "update_rag_status")
    return cast(State, out)

# =========================
# Answer_type: Department_contact
# =========================
def generate_contact_answer(state: State) -> dict:
    """담당자 안내 응답 생성"""
    department = state.get('department_info') or {"name": "인사", "email": "hr@gaida.play.com", "slack": "#ask-hr"}
    response = f"""
해당 문의사항은 **{department['name']}팀**으로 문의하시면 정확하고 빠른 답변을 받으실 수 있습니다.
📧 이메일: {department['email']}
💬 슬랙: {department['slack']}
""".strip()
    return {
        "messages": [AIMessage(content=response)],
        "final_answer": response,
        "execution_path": _append_path(state, "generate_contact_answer"),
    }

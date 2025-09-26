# router.py

import json
from typing import Dict, TypedDict, Literal, Optional, cast

from langchain_core.messages import HumanMessage, SystemMessage

from state import State
from db import get_llm

DEPARTMENTS: Dict[str, Dict[str, str]] = {
    "재무": {"name": "재무", "email": "fi@gaida.play.com", "slack": "#ask-fi"},
    "총무": {"name": "총무", "email": "ga@gaida.play.com", "slack": "#ask-ga"},
    "인프라": {"name": "인프라", "email": "in@gaida.play.com", "slack": "#ask-in"},
    "보안": {"name": "보안", "email": "se@gaida.play.com", "slack": "#ask-se"},
    "인사": {"name": "인사", "email": "hr@gaida.play.com", "slack": "#ask-hr"},
}


class TriageOutput(TypedDict, total=False):
    route: Literal["reject", "rag", "department"]
    department: Optional[str]


def _format_department_reply(dept: Dict[str, str]) -> str:
    return (
        f"해당 문의사항은 {dept['name']}팀으로 문의하시면 정확하고 빠른 답변을 받으실 수 있습니다.\n"
        f"이메일: {dept['email']}\n"
        f"슬랙: {dept['slack']}"
    )


def triage_router(state: State) -> State:
    """
    단일 LLM 분류로 최종 경로를 결정한다.
    - rag: RAG 파이프라인으로 보낸다.
    - department: 여기서 최종 안내 메시지를 생성하고 종료(end) 하도록 세팅한다.
    - reject: 여기서 거절 메시지를 생성하고 종료(end) 하도록 세팅한다.
    """
    question = state.get("refined_question") or state.get("user_question") or ""

    system_prompt = """
당신은 사내 HR 챗봇의 질문 분류 전문가입니다.
질문을 분석해 아래 3가지 중 하나로만 결정하고 JSON으로만 답하세요.

분류 기준
- reject: HR과 무관하거나 지원하지 않는 범주의 질문
- rag: 규정/내규/정책/제도 등 문서 근거로 답이 가능한 일반적 질의
- department: 개인별 처리·승인·신고·민감 상담 등 담당 부서 연결이 적절한 질의

부서 후보: 재무, 총무, 인프라, 보안, 인사

출력 예시
- {"route": "reject"}
- {"route": "rag"}
- {"route": "department", "department": "인사"}
""".strip()

    user_prompt = f'질문: "{question}"\nJSON만 출력'

    llm = get_llm("router")
    messages = [SystemMessage(content=system_prompt), HumanMessage(content=user_prompt)]

    route: Literal["reject", "rag", "department"] = "reject"
    department_name: Optional[str] = None

    try:
        resp = llm.invoke(messages)
        text = (resp.content or "").strip()
        data: TriageOutput = {}
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            # 휴리스틱 폴백
            low = text.lower()
            if "rag" in low:
                data = {"route": "rag"}
            else:
                for dept in DEPARTMENTS.keys():
                    if dept in text:
                        data = {"route": "department", "department": dept}
                        break
            if not data:
                data = {"route": "reject"}
        route = cast(Literal["reject", "rag", "department"], data.get("route", "reject"))
        department_name = cast(Optional[str], data.get("department"))
    except Exception:
        route = "department"
        department_name = "인사"

    # 상태 세팅: rag는 파이프라인 진행, 나머지는 여기서 final_answer 작성 후 종료
    if route == "rag":
        return cast(State, {
            **state,
            "route": "rag",
            "department_info": None,
            "answer_type": "rag_answer",
        })

    if route == "department":
        dept = DEPARTMENTS.get(department_name or "", DEPARTMENTS["인사"])
        return cast(State, {
            **state,
            "route": "department",
            "department_info": dept,
            "final_answer": _format_department_reply(dept),
            "answer_type": "department_contact",
        })

    # reject
    return cast(State, {
        **state,
        "route": "reject",
        "department_info": None,
        "final_answer": "입력하신 질문은 HR 관련 문의가 아니거나 지원 범위를 벗어납니다. HR 관련·규정 기반 문의만 가능합니다.",
        "answer_type": "reject",
    })


def route_after_triage(state: State) -> Literal["rag", "end"]:
    # rag만 파이프라인 진행, 나머지(reject/department)는 end
    return "rag" if state.get("route") == "rag" else "end"

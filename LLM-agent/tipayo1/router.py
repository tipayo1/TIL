# router.py (generalized & composable)

import os
import json
import re
from typing import Dict, TypedDict, Literal, Optional, Any, cast, List

from langchain_core.messages import HumanMessage, SystemMessage
from state import State
from db import get_llm

# -------- Types --------

RouteLiteral = Literal["reject", "rag", "department"]  # default set; can be overridden
class TriageOutput(TypedDict, total=False):
    route: str               # one of allowed routes
    department: Optional[str]  # optional target name
    reason: Optional[str]      # optional short reason

Department = Dict[str, str]   # {"name": str, "email": str, "slack": str, ...}

# -------- Helpers --------

def _load_routes_from_env() -> List[str]:
    raw = os.getenv("ROUTER_ROUTES", "").strip()
    if not raw:
        return ["reject", "rag", "department"]
    try:
        data = json.loads(raw)
        if isinstance(data, list) and all(isinstance(x, str) for x in data):
            return data
    except Exception:
        pass
    return ["reject", "rag", "department"]

def _load_departments_from_env() -> Dict[str, Department]:
    raw = os.getenv("ROUTER_DEPARTMENTS", "").strip()
    if not raw:
        return {}
    try:
        data = json.loads(raw)
        if isinstance(data, dict):
            # normalize values to dict[str,str]
            out: Dict[str, Department] = {}
            for k, v in data.items():
                if isinstance(v, dict):
                    out[k] = {str(kk): str(vv) for kk, vv in v.items()}
            return out
    except Exception:
        pass
    return {}

def _resolve_routes(state: State) -> List[str]:
    # priority: state -> env -> defaults
    routes = state.get("router_routes")
    if isinstance(routes, list) and all(isinstance(x, str) for x in routes):
        return routes  # type: ignore
    return _load_routes_from_env()

def _resolve_departments(state: State) -> Dict[str, Department]:
    # priority: state["router_departments"] or state["departments"] -> env -> {}
    for key in ("router_departments", "departments"):
        maybe = state.get(key)
        if isinstance(maybe, dict):
            # shallow normalize
            out: Dict[str, Department] = {}
            for k, v in maybe.items():
                if isinstance(v, dict):
                    out[k] = {str(kk): str(vv) for kk, vv in v.items()}
            return out
    return _load_departments_from_env()

def _resolve_domain(state: State) -> str:
    # purely cosmetic for prompt wording
    domain = state.get("router_domain") or state.get("context_type")  # e.g., "HR", "legal"
    if isinstance(domain, str) and domain:
        return domain
    return "도메인"

def _format_handoff_reply(name: str, dept: Department) -> str:
    # Generic, not HR-specific
    lines = [
        f"해당 문의는 {dept.get('name', name)}로 연결하는 것이 적절합니다.",
    ]
    if "email" in dept:
        lines.append(f"이메일: {dept['email']}")
    if "slack" in dept:
        lines.append(f"슬랙: {dept['slack']}")
    if "channel" in dept:
        lines.append(f"채널: {dept['channel']}")
    return "\n".join(lines)

def _generic_reject_message(domain: str) -> str:
    return f"요청하신 내용은 현재 {domain} 어시스턴트의 지원 범위를 벗어나거나 적절한 처리 경로가 아닙니다."

_json_obj_pat = re.compile(r"\{.*\}", re.DOTALL)

def _safe_load_json_obj(text: str) -> Optional[dict]:
    # Extract first JSON object
    m = _json_obj_pat.search(text or "")
    if not m:
        return None
    frag = m.group(0)
    try:
        return json.loads(frag)
    except Exception:
        return None

# -------- Core Router --------

def triage_router(state: State) -> State:
    """
    단일 LLM 분류로 최종 경로를 결정한다.
    - rag: RAG 파이프라인으로 보낸다.
    - department: 핸드오프 안내 메시지를 생성하고 종료(end) 하도록 세팅한다.
    - reject: 거절 메시지를 생성하고 종료(end) 하도록 세팅한다.
    라우트/부서 후보는 state 또는 환경에서 주입받아 일반적으로 재사용 가능하다.
    """
    question = state.get("refined_question") or state.get("refined_query") or state.get("query") or state.get("user_question") or ""
    routes = _resolve_routes(state)
    departments = _resolve_departments(state)
    domain = _resolve_domain(state)

    # Build dynamic system prompt (domain-agnostic)
    routes_str = ", ".join(routes)
    dept_names = ", ".join(departments.keys()) if departments else "(없음)"
    system_prompt = f"""
당신은 조직 전반의 질문을 사전 분류하는 에이전트입니다.
다음 라우트 후보 중 하나만 선택하고 JSON으로만 응답하세요.
- routes: [{routes_str}]
- handoff_candidates: [{dept_names}]
규칙:
- "reject": 지원 범위를 벗어나거나 처리 불가한 경우
- "rag": 문서 근거로 답변 생성이 적절한 일반 질의
- "department": 특정 조직/담당으로 핸드오프가 적절한 경우
응답 형식(JSON only):
{{"route": "<one-of-routes>", "department": "<name-optional>", "reason": "<short-optional>"}}
""".strip()

    user_prompt = f'질문: "{question}"\nJSON만 출력'

    llm = get_llm("router")  # role is advisory; model/env drive actual selection
    messages = [SystemMessage(content=system_prompt), HumanMessage(content=user_prompt)]

    decided_route: str = "reject"
    decided_dept: Optional[str] = None

    try:
        resp = llm.invoke(messages)
        text = (getattr(resp, "content", "") or "").strip()

        data = _safe_load_json_obj(text) or {}
        if not isinstance(data, dict) or "route" not in data:
            # heuristic fallback
            low = text.lower()
            # try routes in order
            decided_route = next((r for r in routes if r.lower() in low), "reject")
            if decided_route == "department":
                # find any matching department name
                for dept_name in departments.keys():
                    if dept_name in text:
                        decided_dept = dept_name
                        break
        else:
            decided_route = str(data.get("route") or "reject")
            maybe_dept = data.get("department")
            if isinstance(maybe_dept, str):
                decided_dept = maybe_dept

        # guard unknown route
        if decided_route not in routes:
            decided_route = "reject"
    except Exception:
        # conservative fallback
        decided_route = "reject"
        decided_dept = None

    # State shaping
    if decided_route == "rag":
        return cast(
            State,
            {
                **state,
                "route": "rag",
                "department_info": None,
                "answer_type": "rag_answer",
            },
        )

    if decided_route == "department":
        # choose target or best-effort default (first available)
        if decided_dept and decided_dept in departments:
            target_name = decided_dept
        else:
            target_name = next(iter(departments.keys()), "담당부서")
        dept_info = departments.get(target_name, {"name": target_name})
        return cast(
            State,
            {
                **state,
                "route": "department",
                "department_info": dept_info,
                "final_answer": _format_handoff_reply(target_name, dept_info),
                "answer_type": "department_contact",
            },
        )

    # reject
    return cast(
        State,
        {
            **state,
            "route": "reject",
            "department_info": None,
            "final_answer": _generic_reject_message(domain),
            "answer_type": "reject",
        },
    )

def route_after_triage(state: State) -> Literal["rag", "end"]:
    # rag만 파이프라인 진행, 나머지(reject/department)는 end
    return "rag" if state.get("route") == "rag" else "end"

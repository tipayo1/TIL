# graph.py
# - 명시 노드 + 조건부 엣지(정책 라우팅)
# - expand_search는 힌트만 갱신, 루프는 그래프 담당
# - 체크포인터 주입은 앱 진입점에서 graph.compile(checkpointer=...) 권장

from typing import Any, Dict
from langgraph.graph import StateGraph, END

from state import State
from nodes import (
    compose_rpg,
    intent_parser,
    retrieve_rpg,
    award_xp,
    expand_search,
    rerank,
    plan_answer,
    generate_answer,
)
from policy import decide_after_xp

def _route_after_award(state: Dict[str, Any]) -> str:
    """
    award_xp 이후 경로를 policy로 결정:
    - "expand" -> expand_search
    - "rerank" -> rerank
    - "proceed" -> plan_answer
    """
    decision = decide_after_xp(state)
    if decision == "expand":
        return "expand_search"
    if decision == "rerank":
        return "rerank"
    return "plan_answer"

def build_graph() -> StateGraph:
    g = StateGraph(State)

    # 노드 등록
    g.add_node("compose_rpg", compose_rpg)
    g.add_node("intent_parser", intent_parser)
    g.add_node("retrieve_rpg", retrieve_rpg)
    g.add_node("award_xp", award_xp)
    g.add_node("expand_search", expand_search)
    g.add_node("rerank", rerank)
    g.add_node("plan_answer", plan_answer)
    g.add_node("generate_answer", generate_answer)

    # 엣지 배선
    g.set_entry_point("compose_rpg")
    g.add_edge("compose_rpg", "intent_parser")
    g.add_edge("intent_parser", "retrieve_rpg")
    g.add_edge("retrieve_rpg", "award_xp")

    # 조건부 분기 (정책 일원화)
    g.add_conditional_edges("award_xp", _route_after_award, {
        "expand_search": "expand_search",
        "rerank": "rerank",
        "plan_answer": "plan_answer",
    })

    # 루프: expand -> retrieve -> award
    g.add_edge("expand_search", "retrieve_rpg")

    # rerank 후 계획
    g.add_edge("rerank", "plan_answer")
    g.add_edge("plan_answer", "generate_answer")
    g.add_edge("generate_answer", END)

    return g

# 사용 예시(별도 main/run 모듈 권장):
# from checkpoint_file import FileJSONSaver
# saver = FileJSONSaver()
# app = build_graph().compile(checkpointer=saver)
# result = app.invoke({"messages": [], "query": "..."}, config={"configurable": {"thread_id": "t1"}})
# get_state_history/app.replay 등은 LangGraph persistence 문서 참고.

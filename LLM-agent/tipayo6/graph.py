# graph.py

from langgraph.graph import StateGraph, START, END  # type: ignore
from state import State  # type: ignore
from nodes import (  # type: ignore
    compose_rpg,
    intent_parser,
    retrieve_rpg,
    award_xp,
    expand_search,
    rerank,
    plan_answer,
    generate_answer,
)
from policy import decide_after_xp  # type: ignore
from checkpoint_file import FileJSONSaver  # type: ignore


def build_app():
    """
    경량 단일 목적 RAG 그래프:
    compose → refine → retrieve → award_xp → (expand | rerank) → plan → generate
    """
    builder = StateGraph(State)

    # Nodes
    builder.add_node("compose_rpg", compose_rpg)
    builder.add_node("intent_parser", intent_parser)
    builder.add_node("retrieve_rpg", retrieve_rpg)
    builder.add_node("award_xp", award_xp)
    builder.add_node("expand_search", expand_search)
    builder.add_node("rerank", rerank)
    builder.add_node("plan_answer", plan_answer)
    builder.add_node("generate_answer", generate_answer)

    # Edges
    builder.add_edge(START, "compose_rpg")
    builder.add_edge("compose_rpg", "intent_parser")
    builder.add_edge("intent_parser", "retrieve_rpg")
    builder.add_edge("retrieve_rpg", "award_xp")

    # 정책 분기: decide_after_xp는 "expand" 또는 "rerank"를 반환
    builder.add_conditional_edges(
        "award_xp",
        decide_after_xp,
        {
            "expand": "expand_search",
            "rerank": "rerank",
        },
    )

    # expand 후에는 rerank
    builder.add_edge("expand_search", "rerank")

    # rerank 완료 후 plan → generate → END
    builder.add_edge("rerank", "plan_answer")
    builder.add_edge("plan_answer", "generate_answer")
    builder.add_edge("generate_answer", END)

    # LangGraph는 compile() 된 앱을 실행 대상으로 사용 (파일 기반 체크포인터 포함)
    app = builder.compile(checkpointer=FileJSONSaver())
    return app

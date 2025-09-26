# graph.py

from langgraph.graph import StateGraph, START, END  # type: ignore

from state import State  # type: ignore
from nodes import (  # type: ignore
    compose_rpg,
    intent_parser,
    retrieve_rpg,
    expand_search,
    award_xp,
    rerank,
    plan_answer,
    generate_answer,
)
from policy import decide_after_xp  # type: ignore


def build_app():
    builder = StateGraph(State)

    # Nodes
    builder.add_node("compose_rpg", compose_rpg)
    builder.add_node("intent_parser", intent_parser)
    builder.add_node("retrieve_rpg", retrieve_rpg)
    builder.add_node("expand_search", expand_search)
    builder.add_node("award_xp", award_xp)
    builder.add_node("rerank", rerank)
    builder.add_node("plan_answer", plan_answer)
    builder.add_node("generate_answer", generate_answer)

    # Edges
    builder.add_edge(START, "compose_rpg")
    builder.add_edge("compose_rpg", "intent_parser")
    builder.add_edge("intent_parser", "retrieve_rpg")
    builder.add_edge("retrieve_rpg", "award_xp")

    # Centralized policy-based branching
    builder.add_conditional_edges(
        "award_xp",
        decide_after_xp,
        {
            "expand_search": "expand_search",
            "rerank": "rerank",
        },
    )

    builder.add_edge("expand_search", "rerank")
    builder.add_edge("rerank", "plan_answer")
    builder.add_edge("plan_answer", "generate_answer")
    builder.add_edge("generate_answer", END)

    # IMPORTANT: Do NOT pass a custom checkpointer when using LangGraph API
    # Persistence is handled by the platform (use POSTGRES_URI/POSTGRES_URI_CUSTOM)
    compiled = builder.compile()
    return compiled


# Default app (used by langgraph-api discovery: ./graph.py:graph)
app = build_app()
graph = app


def run_with_thread(input_state: State, thread_id: str):
    """
    동일 thread_id로 호출 시 세션 컨텍스트가 이어집니다.
    """
    return app.invoke(input_state, config={"configurable": {"thread_id": thread_id}})

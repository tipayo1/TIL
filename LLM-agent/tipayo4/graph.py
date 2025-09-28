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

# Studio(dev)용: 내부 영속성을 사용하므로 checkpointer를 넘기지 않습니다.
def build_app():
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

    # 정책 분기: expand 또는 rerank (policy.decide_after_xp가 키를 반환)
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

    # rerank 결과가 비면 expand로 루프백, 그 외 plan으로 진행
    builder.add_conditional_edges(
        "rerank",
        lambda s: "expand" if (s.get("phase") == "expand") else "ok",
        {
            "expand": "expand_search",
            "ok": "plan_answer",
        },
    )

    builder.add_edge("plan_answer", "generate_answer")
    builder.add_edge("generate_answer", END)

    return builder.compile()

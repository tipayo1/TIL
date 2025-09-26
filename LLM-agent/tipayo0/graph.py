# graph.py (UPDATED: policy integration)
from langgraph.graph import StateGraph, START, END
from state import State
from nodes import (
    compose_rpg,
    intent_parser,
    retrieve_rpg,
    expand_search,
    award_xp,
    rerank,
    plan_answer,
    generate_answer,
)
from policy import decide_after_xp  # centralized gating policy

builder = StateGraph(State)

# 노드 등록
builder.add_node("compose_rpg", compose_rpg)
builder.add_node("intent_parser", intent_parser)
builder.add_node("retrieve_rpg", retrieve_rpg)
builder.add_node("expand_search", expand_search)
builder.add_node("award_xp", award_xp)
builder.add_node("rerank", rerank)
builder.add_node("plan_answer", plan_answer)
builder.add_node("generate_answer", generate_answer)

# 시작 엣지
builder.add_edge(START, "compose_rpg")
builder.add_edge("compose_rpg", "intent_parser")

# 파이프라인
builder.add_edge("intent_parser", "retrieve_rpg")
builder.add_edge("retrieve_rpg", "award_xp")

# 중앙화된 정책 기반 분기
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

graph = builder.compile()

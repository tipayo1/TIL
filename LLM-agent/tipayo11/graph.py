# graph.py

from langgraph.graph import StateGraph, START, END
from state import State
from nodes import (
    refine_question,
    retrieve,
    rerank,
    generate_rag_answer,
    verify_rag_answer,
    generate_contact_answer,
    update_hr_status,
    generate_reject_answer,
    update_rag_status,
    compose_rpg,
    award_xp,
    expand_search,
)
from router import route_after_hr, route_after_rag, route_after_award

# ========== 그래프 빌더 ==========
builder = StateGraph(State)

# ========== 노드 등록 ==========
builder.add_node("refine_question", refine_question)

# 1차 라우터
builder.add_node("update_hr_status", update_hr_status)
builder.add_node("generate_reject_answer", generate_reject_answer)  # 터미널

# 2차 라우터 및 담당자 안내
builder.add_node("update_rag_status", update_rag_status)
builder.add_node("generate_contact_answer", generate_contact_answer)  # 터미널

# RPG 경량 계획 + RAG 파이프라인
builder.add_node("compose_rpg", compose_rpg)
builder.add_node("retrieve", retrieve)
builder.add_node("award_xp", award_xp)
builder.add_node("expand_search", expand_search)
builder.add_node("rerank", rerank)
builder.add_node("generate_rag_answer", generate_rag_answer)
builder.add_node("verify_rag_answer", verify_rag_answer)

# ========== 엣지 ==========
builder.add_edge(START, "refine_question")
builder.add_edge("refine_question", "update_hr_status")

# 1차 라우터 분기
builder.add_conditional_edges(
    "update_hr_status",
    route_after_hr,
    {"router2": "update_rag_status", "reject": "generate_reject_answer"},
)

# 2차 라우터 분기
builder.add_conditional_edges(
    "update_rag_status",
    route_after_rag,
    {"rag": "compose_rpg", "department": "generate_contact_answer"},
)

# RPG → RAG
builder.add_edge("compose_rpg", "retrieve")
builder.add_edge("retrieve", "award_xp")

# 메트릭 기반 분기: 확장 또는 재랭크
builder.add_conditional_edges(
    "award_xp",
    route_after_award,
    {"expand": "expand_search", "rerank": "rerank"},
)

# 확장 후 재검색 루프
builder.add_edge("expand_search", "retrieve")

# RAG 파이프라인
builder.add_edge("rerank", "generate_rag_answer")
builder.add_edge("generate_rag_answer", "verify_rag_answer")
builder.add_edge("verify_rag_answer", END)

# 터미널 경로
builder.add_edge("generate_contact_answer", END)
builder.add_edge("generate_reject_answer", END)

# ========== 공개 그래프 ==========
graph = builder.compile()

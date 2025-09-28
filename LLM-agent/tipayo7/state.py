# state.py (UPDATED: RPG versioning & validation fields + router fields)

from typing import Literal, Optional, Dict, List, Any
from langgraph.graph import MessagesState
from langchain_core.documents import Document


class State(MessagesState, total=False):
    """RPG 내재화형 RAG 상태"""

    # 사용자 질문/정제 질의
    query: str
    refined_query: str

    # 검색 힌트/결과
    retrieval_hints: Dict[str, Optional[Any]]
    retrieved_docs: List[Document]
    retrieval_metrics: Dict[str, Any]  # {k, n, avg_score, coverage, diversity, ...}

    # 증거 계획 및 최종 답변
    # 각 항목은 RPG 구현 레벨 계획을 반영
    # - claim: 생성할 문장의 핵심 주장
    # - evidence: 근거 문서 인덱스 목록
    # - target_component/interface_contract: I/O 계약(입력, 출력)
    # - required_inputs/validation: 필수 입력과 검증 규칙
    answer_plan: List[Dict[str, Any]]
    answer: str

    # 진행상태/경험치/로그
    phase: Literal["setup", "refine", "search", "expand", "rerank", "plan", "answer", "end"]
    xp: int
    fail_count: int
    log: List[Dict[str, Any]]

    # RPG core
    # {"graph": {...}, "registry": {...}, "flows": [...]}
    rpg: Dict[str, Any]
    execution_path: List[str]  # ["intent_parser", "retrieve_rpg", ...]
    plugins: List[str]

    # Context & validation
    context_type: Literal["general", "legal", "technical", "conversational"]
    flow_violations: List[Dict[str, Any]]

    # RPG persistence/versioning
    # [{ "version": int, "graph": {...}, "ts": float, "note": str }]
    rpg_versions: List[Dict[str, Any]]
    rpg_version: int  # current version counter

    # Router fields (미사용 시 무시)
    route: Literal["rag", "department", "reject"]
    department_info: Dict[str, str]
    final_answer: str
    answer_type: Literal["rag_answer", "department_contact", "reject"]

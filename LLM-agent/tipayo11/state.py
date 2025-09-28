# state.py

from typing import Literal, Optional, Dict, List, Any
from langgraph.graph import MessagesState
from langchain_core.documents import Document

class State(MessagesState, total=False):
    """HR 챗봇 메인 상태 클래스 (경량 RPG 통합)"""

    # === 사용자 질문 전처리 ===
    user_question: str                    # 원본 질문
    refined_question: str                 # LLM 정제 질문

    # === 1차 라우터: HR 관련 질문 판단 ===
    is_hr_question: bool                  # True: HR 관련, False: 비관련

    # === 2차 라우터: 답변 방식 결정 ===
    is_rag_suitable: bool                 # True: RAG, False: 담당자

    # === 담당자 안내 정보 ===
    department_info: Optional[Dict[str, str]]

    # === RAG 처리 ===
    retrieved_docs: List[Document]

    # === 답변 검증 ===
    verification: str

    # === 최종 답변 통합 ===
    answer_type: Literal[
        "pending",          # 1차 라우터 True
        "reject",           # 1차 라우터 False
        "rag_answer",       # 2차 라우터 True
        "department_contact" # 2차 라우터 False
    ]
    final_answer: str

    # === 경량 RPG: 계획/메트릭/경로/확장 ===
    rpg_plan: Dict[str, Any]             # {"query": str, "strategies": {"retrieval": {"k": int}, ...}}
    retrieval_metrics: Dict[str, Any]    # {"k": int, "n": int, "coverage": float, "diversity": float, "avgscore": float}
    xp: int                              # 확장(Expand) 수행 횟수
    execution_path: List[str]            # 실행된 노드 이름 순서

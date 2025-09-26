# state.py (RPG: versioning & validation & feature tree)

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
    retrieval_metrics: Dict[str, Any]  # {k, n, avg_score, coverage, diversity, intent_coverage, negative_rate, novel_evidence_contrib}

    # 증거 계획 및 최종 답변
    answer_plan: List[Dict[str, Any]]  # [{"claim": str, "evidence": [int]}]
    answer: str

    # 진행상태/경험치/로그
    phase: Literal["setup", "refine", "search", "expand", "rerank", "plan", "answer", "end"]
    xp: int
    fail_count: int
    log: List[Dict[str, Any]]

    # RPG core
    rpg: Dict[str, Any]  # {"graph": {...}, "registry": {...}, "flows": [...]}
    execution_path: List[str]  # ["intent_parser", "retrieve_rpg", ...]
    plugins: List[str]

    # Context & validation
    context_type: Literal["general", "legal", "technical", "conversational"]
    flow_violations: List[Dict[str, Any]]

    # RPG persistence/versioning
    rpg_versions: List[Dict[str, Any]]  # [{ "version": int, "graph": {...}, "ts": float, "note": str }]
    rpg_version: int  # current version counter

    # Feature tree / selection
    feature_tree: Dict[str, Any]  # {"roots":[...]} serialized FeatureTree
    subtree_choice: Dict[str, Any]  # {"retrieval": "semantic|hybrid|expand", ...}

    # Router fields (kept for compatibility)
    route: Literal["rag", "department", "reject"]
    department_info: Dict[str, str]
    final_answer: str
    answer_type: Literal["rag_answer", "department_contact", "reject"]

    # Testing / CI-lite
    test_results: Dict[str, Any]

    # Threading / persistence key
    thread_id: str

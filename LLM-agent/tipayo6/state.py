# state.py
# - LangGraph MessagesState 확장 + Annotated 리듀서 적용
# - RPG-Lite 신호(전략·온톨로지·정책·흐름)를 상태로 내재화

from typing import Literal, Optional, Dict, List, Any
from typing import Annotated
import operator

from langgraph.graph import MessagesState
from langchain_core.documents import Document


class State(MessagesState, total=False):
    """
    RPG-Lite 내재화형 RAG 상태.
    - 질의/정제 질의, 검색 힌트, 템플릿/온톨로지 힌트
    - 검색 결과/메트릭, 단계 계획/최종 답변/출처
    - 라우팅/학습 신호(xp), 로그, 실행 경로
    """

    # 입력/전처리
    query: str
    refined_query: str

    # 검색 힌트/전략 파라미터 (k, weights, filters 등)
    retrieval_hints: Dict[str, Optional[Any]]

    # 템플릿/온톨로지 힌트
    template_hints: Dict[str, Any]
    ontology_version: str
    ontology_entities: Dict[str, Any]  # {"entities": [...], "domain": "..."}

    # 검색 결과/메트릭
    retrieved_docs: List[Document]
    retrieval_metrics: Dict[str, Any]  # {k, n, avg_score, coverage, diversity, intent_coverage, negative_rate, novel_evidence_contrib, ontology_coverage}

    # 계획/응답/출처
    answer_plan: List[Dict[str, Any]]  # [{"claim": str, "evidence": [int]}]
    answer: str
    sources: List[str]
    citation_policy: Dict[str, Any]  # {"enable": bool, "max": int, "inline": bool, "append_section": bool, "label": str}

    # 진행/학습/로그
    phase: Literal["setup", "refine", "search", "expand", "rerank", "plan", "answer", "end"]
    xp: int
    xp_total: float
    fail_count: int
    log: Annotated[List[Dict[str, Any]], operator.add]  # 누적

    # RPG 메타 (경량): 버전/레지스트리 스냅샷/흐름 로그
    rpg: Dict[str, Any]  # {"version": str, "registry": {...}, "flows": [...]}

    # Studio 가시화용 실행 경로 누적
    execution_path: Annotated[List[str], operator.add]

    # 관측/중복 방지
    seen_doc_ids: Annotated[List[str], operator.add]

    # 선택적 FeatureTree 경량 프로필 (도메인·전략·임계값)
    feature_tree_lite: Dict[str, Any]

    # 루프 제어/분기 신호(선택 필드)
    expand_count: int
    flat_rounds: int
    k_zero_rounds: int
    last_coverage: float
    stagnant_rounds: int

# policy.py
# - 분기/임계값 중앙 일원화
# - 모든 expand / rerank / proceed 결정은 여기서만 수행
# - 환경 변수로 운영 튜닝

import os
import random
from typing import Dict, Any

def _float_env(name: str, default: float) -> float:
    try:
        return float(os.getenv(name, str(default)))
    except Exception:
        return default

def _bool_env(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip() not in ("0", "false", "False", "no", "NO")

# 중앙 임계치 (환경 조정)
COVERAGE_TH = _float_env("RPG_COVERAGE_TH", 0.4)
DIVERSITY_TH = _float_env("RPG_DIVERSITY_TH", 0.4)
INTENT_COVERAGE_TH = _float_env("RPG_INTENT_COVERAGE_TH", 0.5)
NEGATIVE_RATE_MAX = _float_env("RPG_NEGATIVE_RATE_MAX", 0.6)
NOVEL_EVIDENCE_TH = _float_env("RPG_NOVEL_EVIDENCE_TH", 0.1)
ONTOLOGY_COVERAGE_TH = _float_env("RPG_ONTOLOGY_COVERAGE_TH", 0.5)

# 탐험도(ε-greedy)
EPSILON = _float_env("RPG_EPSILON", 0.15)

# FeatureTree 개입 여부/여지
FT_DECIDES = _bool_env("RAG_FEATURETREE_DECIDES", True)
TIE_MARGIN = _float_env("RAG_TIE_MARGIN", 0.05)  # 모호성 밴드
DECIDE_EPS_SCALE = _float_env("RAG_DECIDE_EPS_SCALE", 0.5)  # FT 개입시 ε 축소

def need_expand(metrics: Dict[str, Any]) -> bool:
    """
    expand 필요성 판단(폭 ↑):
    - coverage/diversity/intent_coverage 낮음
    - novel_evidence_contrib 높음
    - negative_rate 과다
    - ontology_coverage 낮음
    """
    cov = float(metrics.get("coverage", 0.0))
    div = float(metrics.get("diversity", 0.0))
    intent_cov = float(metrics.get("intent_coverage", 0.0))
    neg_rate = float(metrics.get("negative_rate", 0.0))
    novel = float(metrics.get("novel_evidence_contrib", 0.0))
    onto_cov = float(metrics.get("ontology_coverage", 0.0))

    if neg_rate > NEGATIVE_RATE_MAX:
        return True
    if cov < COVERAGE_TH or div < DIVERSITY_TH or intent_cov < INTENT_COVERAGE_TH:
        return True
    if novel > NOVEL_EVIDENCE_TH:
        return True
    if onto_cov < ONTOLOGY_COVERAGE_TH:
        return True
    return False

def decide_after_xp(state: Dict[str, Any]) -> str:
    """
    award_xp 이후 다음 경로:
    - "expand": 탐색 폭 확장
    - "rerank": 정밀화 단계
    - "proceed": 계획/생성으로 진행
    - ε-greedy로 소량 탐험 유지
    - FT 프로필이 모호성 구간에서 tie-breaker로 개입
    """
    metrics = state.get("retrieval_metrics", {}) or {}
    xp_total = float(state.get("xp_total", 0.0))
    ft = state.get("feature_tree_lite", {}) or {}

    # ε 탐험
    eps = EPSILON * (DECIDE_EPS_SCALE if FT_DECIDES and ft else 1.0)
    if random.random() < eps:
        return "expand"

    # FT tie-breaker
    if FT_DECIDES and ft:
        prefer = (ft.get("routing") or {}).get("prefer", "")
        amb = abs(float(metrics.get("coverage", 0.0)) - float(metrics.get("diversity", 0.0))) <= TIE_MARGIN
        if amb and prefer in ("expand", "rerank"):
            return prefer

    # 표준 결정
    if need_expand(metrics):
        return "expand"

    good_cov = float(metrics.get("coverage", 0.0)) >= COVERAGE_TH
    good_intent = float(metrics.get("intent_coverage", 0.0)) >= INTENT_COVERAGE_TH
    low_neg = float(metrics.get("negative_rate", 0.0)) <= NEGATIVE_RATE_MAX
    good_onto = float(metrics.get("ontology_coverage", 0.0)) >= ONTOLOGY_COVERAGE_TH

    if good_cov and good_intent and low_neg and good_onto and xp_total >= 1.0:
        return "proceed"
    return "rerank"

# .env 참고(README 권장):
# - RPG_COVERAGE_TH, RPG_DIVERSITY_TH, RPG_INTENT_COVERAGE_TH, RPG_EPSILON, ...
# - RAG_FEATURETREE_DECIDES, RAG_TIE_MARGIN, RAG_DECIDE_EPS_SCALE

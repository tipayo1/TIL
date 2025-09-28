# router.py

import os
from typing import Literal
from state import State

def _float_env(name: str, default: float) -> float:
    try:
        return float(os.getenv(name, str(default)))
    except Exception:
        return default

# =========================
# 1차 라우터: HR Router
# =========================
def route_after_hr(state: State) -> str:
    """HR 판별 결과에 따라 다음 노드 결정"""
    return "router2" if state["is_hr_question"] else "reject"

# =========================
# 2차 라우터: RAG vs Department
# =========================
def route_after_rag(state: State) -> Literal["rag", "department"]:
    """RAG 사용 여부에 따라 다음 노드 결정"""
    return "rag" if state.get('is_rag_suitable') else "department"

# =========================
# 3차 라우터: RPG 확장 vs 재랭크
# =========================
def route_after_award(state: State) -> Literal["expand", "rerank"]:
    """retrieval_metrics와 xp를 근거로 확장 또는 재랭크 선택"""
    met = state.get("retrieval_metrics") or {}
    coverage_th = _float_env("RPG_COVERAGE_TH", 0.5)
    diversity_th = _float_env("RPG_DIVERSITY_TH", 0.4)
    max_xp = int(os.getenv("RPG_MAX_EXPAND", "2"))

    coverage = float(met.get("coverage", 0.0))
    diversity = float(met.get("diversity", 0.0))
    xp = int(state.get("xp", 0))

    if (coverage < coverage_th or diversity < diversity_th) and (xp < max_xp):
        return "expand"
    return "rerank"

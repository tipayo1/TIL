# policy.py

import os
from typing import Dict, Any, List

def _float_env(name: str, default: float) -> float:
    try:
        return float(os.getenv(name, str(default)))
    except Exception:
        return default

# Centralized thresholds
COVERAGE_TH = _float_env("RPG_COVERAGE_TH", 0.4)
DIVERSITY_TH = _float_env("RPG_DIVERSITY_TH", 0.4)
INTENT_COVERAGE_TH = _float_env("RPG_INTENT_COVERAGE_TH", 0.5)
NEG_RATE_MAX = _float_env("RPG_NEG_RATE_MAX", 0.6)
NOVEL_CONTRIB_TH = _float_env("RPG_NOVEL_EVIDENCE_TH", 0.1)
EPSILON = _float_env("RPG_EPSILON", 0.15)

AB_POLICY = os.getenv("RPG_AB_POLICY", "A")  # "A" or "B"

def need_expand(metrics: Dict[str, Any]) -> bool:
    n = int(metrics.get("n") or 0)
    coverage = float(metrics.get("coverage") or 0.0)
    diversity = float(metrics.get("diversity") or 0.0)
    intent_cov = float(metrics.get("intent_coverage") or 0.0)
    neg_rate = float(metrics.get("negative_rate") or 0.0)
    # Expand if no docs or poor coverage/diversity or poor intent alignment or high negatives
    return (n == 0) or (coverage < COVERAGE_TH) or (diversity < DIVERSITY_TH) or (intent_cov < INTENT_COVERAGE_TH) or (neg_rate > NEG_RATE_MAX)

def next_in_path(execution_path: List[str], candidates: List[str]) -> str:
    order = {name: i for i, name in enumerate(execution_path or [])}
    best = None
    best_rank = 10**9
    for c in candidates:
        r = order.get(c, 10**8)
        if r < best_rank:
            best, best_rank = c, r
    return best or candidates[0]

def decide_after_xp(state: Dict[str, Any]) -> str:
    """
    LangGraph conditional edge callback for 'award_xp' node.
    Returns next node key: 'expand_search' or 'rerank'.
    """
    met = state.get("retrieval_metrics") or {}
    candidates = ["expand_search", "rerank"]

    # Safety rails first
    if need_expand(met):
        return "expand_search"

    avg_score = float(met.get("avg_score") or 0.0)
    coverage = float(met.get("coverage") or 0.0)
    n = int(met.get("n") or 0)
    intent_cov = float(met.get("intent_coverage") or 0.0)
    novel = float(met.get("novel_evidence_contrib") or 0.0)
    preferred = next_in_path(state.get("execution_path") or [], candidates)

    if AB_POLICY == "A":
        # strict: require intent + coverage sufficient, else expand
        if (coverage >= COVERAGE_TH) and (intent_cov >= INTENT_COVERAGE_TH) and (avg_score >= 0.1 or n >= 5):
            return preferred if preferred in candidates else "rerank"
        return "expand_search"
    else:
        # permissive with novelty encouragement
        if (coverage >= COVERAGE_TH) and (avg_score >= 0.1 or n >= 5):
            if novel < NOVEL_CONTRIB_TH:
                return "expand_search"
            return preferred if preferred in candidates else "rerank"
        return preferred if preferred in candidates else "rerank"

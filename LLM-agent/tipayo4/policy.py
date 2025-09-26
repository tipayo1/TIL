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

def need_expand(metrics: Dict[str, Any]) -> bool:
    n = int(metrics.get("n") or 0)
    coverage = float(metrics.get("coverage") or 0.0)
    diversity = float(metrics.get("diversity") or 0.0)
    return (n == 0) or (coverage < COVERAGE_TH) or (diversity < DIVERSITY_TH)

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

    # Safety rails
    if need_expand(met):
        return "expand_search"

    # Prefer planned execution_path when metrics are acceptable
    avg_score = float(met.get("avg_score") or 0.0)
    coverage = float(met.get("coverage") or 0.0)
    n = int(met.get("n") or 0)
    preferred = next_in_path(state.get("execution_path") or [], candidates)

    if (coverage >= COVERAGE_TH) and (avg_score >= 0.1 or n >= 5):
        return preferred if preferred in candidates else "rerank"

    return preferred if preferred in candidates else "rerank"

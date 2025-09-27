# policy.py

import os
from typing import Dict, Any, Union

def _float_env(name: str, default: float) -> float:
    try:
        return float(os.getenv(name, str(default)))
    except Exception:
        return default

# Centralized thresholds (env-tunable)
COVERAGE_TH = _float_env("RPG_COVERAGE_TH", 0.4)
DIVERSITY_TH = _float_env("RPG_DIVERSITY_TH", 0.4)
INTENT_COVERAGE_TH = _float_env("RPG_INTENT_COVERAGE_TH", 0.5)
NEGATIVE_RATE_MAX = _float_env("RPG_NEGATIVE_RATE_MAX", 0.6)
NOVEL_EVIDENCE_TH = _float_env("RPG_NOVEL_EVIDENCE_TH", 0.1)
EPSILON = _float_env("RPG_EPSILON", 0.15)

# Simple A/B policy toggle (kept minimal)
AB_POLICY = os.getenv("RPG_AB_POLICY", "A")  # "A" or "B"

def need_expand(metrics: Dict[str, Any]) -> bool:
    """
    Decide whether to expand retrieval based on coverage/diversity/intent/negatives.
    Expects keys: n, coverage, diversity, intent_coverage, negative_rate
    """
    n = int(metrics.get("n") or 0)
    coverage = float(metrics.get("coverage") or 0.0)
    diversity = float(metrics.get("diversity") or 0.0)
    intent_cov = float(metrics.get("intent_coverage") or 0.0)
    neg_rate = float(metrics.get("negative_rate") or 0.0)

    # Expand if no docs or poor coverage/diversity or poor intent alignment or high negatives.
    return (
        n == 0
        or coverage < COVERAGE_TH
        or diversity < DIVERSITY_TH
        or intent_cov < INTENT_COVERAGE_TH
        or neg_rate > NEGATIVE_RATE_MAX
    )

def _tuned_need_expand(metrics: Dict[str, Any]) -> bool:
    """
    Minimal A/B tuning without changing external behavior or signatures.
    Policy B: slightly stricter thresholds to encourage one more expand step.
    """
    n = int(metrics.get("n") or 0)
    coverage = float(metrics.get("coverage") or 0.0)
    diversity = float(metrics.get("diversity") or 0.0)
    intent_cov = float(metrics.get("intent_coverage") or 0.0)
    neg_rate = float(metrics.get("negative_rate") or 0.0)

    if AB_POLICY.upper() == "B":
        cov_th = COVERAGE_TH + 0.05
        div_th = DIVERSITY_TH + 0.05
        intent_th = INTENT_COVERAGE_TH + 0.05
        neg_max = NEGATIVE_RATE_MAX  # keep negatives unchanged for stability
    else:
        cov_th = COVERAGE_TH
        div_th = DIVERSITY_TH
        intent_th = INTENT_COVERAGE_TH
        neg_max = NEGATIVE_RATE_MAX

    return (
        n == 0
        or coverage < cov_th
        or diversity < div_th
        or intent_cov < intent_th
        or neg_rate > neg_max
    )

def decide_after_xp(state_or_metrics: Union[Dict[str, Any], Any]) -> str:
    """
    Conditional edge function for LangGraph.
    Accepts either:
      - full state dict containing retrieval_metrics, or
      - a metrics dict directly.
    Returns the next node key: "expandsearch" or "rerank".
    """
    # Try to extract metrics from state-like dict
    metrics: Dict[str, Any] = {}
    if isinstance(state_or_metrics, dict):
        if "retrieval_metrics" in state_or_metrics and isinstance(state_or_metrics["retrieval_metrics"], dict):
            metrics = state_or_metrics["retrieval_metrics"]  # state path
        else:
            metrics = state_or_metrics  # treat as metrics dict

    # Fallback to empty metrics for safety (interpreted as poor coverage -> expand)
    if not isinstance(metrics, dict):
        metrics = {}

    expand = _tuned_need_expand(metrics)
    return "expandsearch" if expand else "rerank"

# Backward-compat alias (some graphs may import without underscore)
decideafterxp = decide_after_xp

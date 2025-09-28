# policy.py

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

# ---------------- Centralized thresholds (env-tunable) ----------------

COVERAGE_TH = _float_env("RPG_COVERAGE_TH", 0.4)
DIVERSITY_TH = _float_env("RPG_DIVERSITY_TH", 0.4)
INTENT_COVERAGE_TH = _float_env("RPG_INTENT_COVERAGE_TH", 0.5)
NEGATIVE_RATE_MAX = _float_env("RPG_NEGATIVE_RATE_MAX", 0.6)
NOVEL_EVIDENCE_TH = _float_env("RPG_NOVEL_EVIDENCE_TH", 0.1)

# Exploration rate for routing
EPSILON = _float_env("RPG_EPSILON", 0.15)

# Simple A/B policy toggle (kept minimal)
AB_POLICY = os.getenv("RPG_AB_POLICY", "A") # "A" or "B"

# FeatureTree involvement toggles
FT_DECIDES = _bool_env("RAG_FEATURETREE_DECIDES", True) # enable tie-breaker
TIE_MARGIN = _float_env("RAG_TIE_MARGIN", 0.05) # ambiguity band
DECIDE_EPS_SCALE = _float_env("RAG_DECIDE_EPS_SCALE", 0.5) # shrink epsilon when FT used

def need_expand(metrics: Dict[str, Any]) -> bool:
    """
    Decide whether to expand retrieval based on coverage/diversity/intent/negatives/novelty.
    Expects keys: n, k, coverage, diversity, intent_coverage, negative_rate, novel_evidence_contrib
    """
    n = int(metrics.get("n") or 0)
    coverage = float(metrics.get("coverage") or 0.0)
    diversity = float(metrics.get("diversity") or 0.0)
    intent_cov = float(metrics.get("intent_coverage") or 0.0)
    neg_rate = float(metrics.get("negative_rate") or 0.0)
    novel = float(metrics.get("novel_evidence_contrib") or 0.0)
    k = int(metrics.get("k") or 8)

    if n == 0:
        return True
    if coverage < COVERAGE_TH:
        return True
    if diversity < DIVERSITY_TH:
        return True
    if intent_cov < INTENT_COVERAGE_TH:
        return True
    if neg_rate > NEGATIVE_RATE_MAX:
        return True
    if novel < NOVEL_EVIDENCE_TH and n < k:
        return True
    return False

def _is_ambiguous(metrics: Dict[str, Any]) -> bool:
    """
    Returns True when metrics are near decision boundaries → allow tie-breaking.
    """
    coverage = float(metrics.get("coverage") or 0.0)
    diversity = float(metrics.get("diversity") or 0.0)
    intent_cov = float(metrics.get("intent_coverage") or 0.0)
    neg_rate = float(metrics.get("negative_rate") or 0.0)

    near_cov = abs(coverage - COVERAGE_TH) <= TIE_MARGIN
    near_div = abs(diversity - DIVERSITY_TH) <= TIE_MARGIN
    near_int = abs(intent_cov - INTENT_COVERAGE_TH) <= TIE_MARGIN
    near_neg = abs(neg_rate - NEGATIVE_RATE_MAX) <= TIE_MARGIN
    return near_cov or near_div or near_int or near_neg

def decide_after_xp(state: Dict[str, Any]) -> str:
    """
    Conditional router used by the graph after initial retrieval.
    Must return one of: "expand" or "rerank"
    """
    metrics: Dict[str, Any] = dict(state.get("retrieval_metrics") or {})
    subtree_choice = (state.get("subtree_choice") or {})
    ft_pick_retr = str(subtree_choice.get("retrieval") or "").lower()
    ft_pick_decision = str(subtree_choice.get("decision") or "").lower()

    base_expand = need_expand(metrics)
    decision = "expand" if base_expand else "rerank"

    # A/B policy: B favors mild expansion a bit more under weak evidence
    if AB_POLICY == "B" and not base_expand:
        if float(metrics.get("coverage") or 0.0) < COVERAGE_TH + 0.05:
            decision = "expand"

    # Ambiguity + FeatureTree tie-break
    ft_used = False
    if _is_ambiguous(metrics) and FT_DECIDES:
        # Prefer explicit FT decision if present
        if ft_pick_decision in ("expand", "rerank"):
            decision = ft_pick_decision
            ft_used = True
        else:
            # Backward-compatible: infer from retrieval choice
            if ft_pick_retr == "expand":
                decision = "expand"
                ft_used = True
            elif ft_pick_retr in ("hybrid", "semantic"):
                decision = "rerank"
                ft_used = True

    # Exploration probability (reduced when FT tie-break used)
    eps = EPSILON * (DECIDE_EPS_SCALE if ft_used else 1.0)
    import random as _rnd
    if _rnd.random() < max(0.0, min(1.0, eps)):
        decision = "expand"

    return decision

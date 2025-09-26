# rpg.py (UPDATED: policy integration)
from __future__ import annotations

import os
import json
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Tuple
from abc import ABC, abstractmethod

from policy import need_expand, COVERAGE_TH, DIVERSITY_TH  # centralized policy

# -----------------------------
# Config (env-driven overrides)
# -----------------------------
def _float_env(name: str, default: float) -> float:
    try:
        return float(os.getenv(name, str(default)))
    except Exception:
        return default

def _load_json_env(name: str) -> Optional[dict]:
    raw = os.getenv(name)
    if not raw:
        return None
    try:
        return json.loads(raw)
    except Exception:
        return None

DEFAULT_PATH = json.loads(
    os.getenv(
        "RPG_DEFAULT_PATH",
        '["intent_parser","retrieve_rpg","rerank","plan_answer","generate_answer"]',
    )
)

# -----------------------------
# RPG Nodes / Graph (lightweight)
# -----------------------------
def _prune_meta(meta: Dict[str, Any], max_kv: int = 16) -> Dict[str, Any]:
    """Keep only small scalar/meta keys to avoid oversized payloads."""
    out: Dict[str, Any] = {}
    for k, v in meta.items():
        if isinstance(v, (str, int, float, bool)) and len(str(v)) < 200:
            out[k] = v
    return out

@dataclass(slots=True)
class RPGNode:
    name: str
    node_type: str  # "capability" | "component" | "function"
    children: List["RPGNode"] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)  # names
    data_flows: List[Dict[str, Any]] = field(default_factory=list)
    meta: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "type": self.node_type,
            "dependencies": list(self.dependencies),
            "data_flows": list(self.data_flows),
            "meta": _prune_meta(dict(self.meta)),
            "children": [c.to_dict() for c in self.children],
        }

@dataclass(slots=True)
class RPGGraph:
    root_nodes: List[RPGNode] = field(default_factory=list)
    meta: Dict[str, Any] = field(default_factory=dict)

    def add_root(self, node: RPGNode) -> None:
        self.root_nodes.append(node)

    def to_dict(self) -> Dict[str, Any]:
        return {"meta": _prune_meta(dict(self.meta)), "roots": [r.to_dict() for r in self.root_nodes]}

    def suggest_execution_path(self, metrics: Optional[Dict[str, Any]] = None) -> List[str]:
        """
        Provide a recommended path; LangGraph execution remains the source of truth.
        """
        m = metrics or {}
        path = ["intent_parser", "retrieve_rpg"]
        if need_expand(m):
            path.append("expand_search")
        path += ["rerank", "plan_answer", "generate_answer"]
        return path

# -----------------------------
# Registry and Binding
# -----------------------------
class RAGComponentRegistry:
    def __init__(self):
        # defaults
        self.retrieval_strategies: Dict[str, Dict[str, Any]] = {
            "semantic": {"name": "semantic", "k": 8},
            "expand": {"name": "expand", "k": 16},
            "hybrid": {"name": "hybrid", "k": 12, "bm25_weight": 0.4, "dense_weight": 0.6},
            "legal": {"name": "legal", "k": 12, "section_boost": True},
            "technical": {"name": "technical", "k": 10, "code_boost": True},
            "conversational": {"name": "conversational", "k": 8, "history_boost": True},
        }
        self.rerankers: Dict[str, Dict[str, Any]] = {
            "cross_encoder": {"name": "cross_encoder"},
            "none": {"name": "none"},
            "llm_based": {"name": "llm_based"},
        }
        self.generators: Dict[str, Dict[str, Any]] = {
            "evidence_based": {"name": "evidence_based"},
            "template": {"name": "template"},
            "cot": {"name": "chain_of_thought"},
        }
        # optional env overrides (json)
        if (ov := _load_json_env("RAG_STRATEGIES_JSON")):
            self.retrieval_strategies.update(ov.get("retrieval", {}))
            self.rerankers.update(ov.get("rerankers", {}))
            self.generators.update(ov.get("generators", {}))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "retrieval": self.retrieval_strategies,
            "rerankers": self.rerankers,
            "generators": self.generators,
        }

def bind_registry_to_hints(
    registry: Dict[str, Any],
    context_type: str,
    base_hints: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Choose retrieval/rerank/generation config by context and merge into hints.
    """
    hints = dict(base_hints or {})
    retr_map = registry.get("retrieval", {})
    rer_map = registry.get("rerankers", {})
    gen_map = registry.get("generators", {})

    if context_type == "legal":
        chosen = retr_map.get("legal") or retr_map.get("hybrid") or retr_map.get("semantic")
        rer = rer_map.get("cross_encoder")
        gen = gen_map.get("evidence_based")
    elif context_type == "technical":
        chosen = retr_map.get("technical") or retr_map.get("hybrid") or retr_map.get("semantic")
        rer = rer_map.get("llm_based") or rer_map.get("cross_encoder")
        gen = gen_map.get("evidence_based")
    elif context_type == "conversational":
        chosen = retr_map.get("conversational") or retr_map.get("semantic")
        rer = rer_map.get("none")
        gen = gen_map.get("template") or gen_map.get("evidence_based")
    else:
        chosen = retr_map.get("hybrid") or retr_map.get("semantic")
        rer = rer_map.get("cross_encoder")
        gen = gen_map.get("evidence_based")

    if chosen:
        hints.update({"strategy": chosen.get("name"), "k": chosen.get("k", hints.get("k", 8))})
        for key in ("bm25_weight", "dense_weight", "section_boost", "code_boost", "history_boost"):
            if key in chosen:
                hints[key] = chosen[key]
    if rer:
        hints["reranker"] = rer.get("name")
    if gen:
        hints["generator"] = gen.get("name")
    return hints

# -----------------------------
# Data Flow contracts
# -----------------------------
class DataFlowManager:
    """
    Describe payload schemas and validate runtime state against contracts.
    """
    def __init__(self):
        self.schemas: Dict[Tuple[str, str], Dict[str, Any]] = {
            ("intent_parser", "retrieve_rpg"): {"required": ["refined_query", "retrieval_hints"]},
            ("retrieve_rpg", "award_xp"): {"required": ["retrieved_docs", "retrieval_metrics"]},
            ("award_xp", "expand_search"): {"required": ["retrieval_metrics"]},
            ("award_xp", "rerank"): {"required": ["retrieved_docs"]},
            ("expand_search", "rerank"): {"required": ["retrieved_docs", "retrieval_metrics"]},
            ("rerank", "plan_answer"): {"required": ["retrieved_docs"]},
            ("plan_answer", "generate_answer"): {"required": ["answer_plan", "retrieved_docs"]},
        }

    def describe(self) -> List[Dict[str, Any]]:
        return [{"from": frm, "to": to, "schema": sch} for (frm, to), sch in self.schemas.items()]

    def validate(self, frm: str, to: str, state: Dict[str, Any]) -> Dict[str, Any]:
        schema = self.schemas.get((frm, to))
        violations: List[str] = []
        if not schema:
            return {"ok": True, "violations": violations}
        required = schema.get("required", [])
        for key in required:
            if key not in state or state.get(key) is None:
                violations.append(f"Missing required '{key}' for flow {frm} -> {to}")
        return {"ok": len(violations) == 0, "violations": violations}

def unit_test_flow_assertions(dfm: DataFlowManager) -> List[str]:
    """Simple static checks for schema coherence."""
    issues: List[str] = []
    for desc in dfm.describe():
        schema = desc["schema"]
        if not isinstance(schema, dict) or "required" not in schema:
            issues.append(f"Schema invalid for {desc['from']}->{desc['to']}")
    return issues

# -----------------------------
# Domain graph builders
# -----------------------------
def build_general_rag_graph(query: str) -> RPGGraph:
    understand = RPGNode("QueryUnderstanding", "capability")
    retrieve = RPGNode("Retrieval", "capability", dependencies=["QueryUnderstanding"])
    rerank = RPGNode("Rerank", "capability", dependencies=["Retrieval"])
    plan = RPGNode("Plan", "capability", dependencies=["Rerank"])
    answer = RPGNode("Answer", "capability", dependencies=["Plan"])

    retrieve_sem = RPGNode("SemanticRetrieval", "component", meta={"k": 8})
    retrieve_exp = RPGNode("ExpandedRetrieval", "component", meta={"k": 16})
    retrieve.children = [retrieve_sem, retrieve_exp]

    graph = RPGGraph(
        root_nodes=[understand, retrieve, rerank, plan, answer],
        meta={"query": (query or ""), "style": "general-evidence-based"},
    )
    return graph

def build_legal_rag_graph(query: str) -> RPGGraph:
    g = build_general_rag_graph(query)
    g.meta["domain"] = "legal"
    for r in g.root_nodes:
        if r.name == "Retrieval":
            r.meta["section_boost"] = True
    return g

def build_technical_rag_graph(query: str) -> RPGGraph:
    g = build_general_rag_graph(query)
    g.meta["domain"] = "technical"
    for r in g.root_nodes:
        if r.name == "Retrieval":
            r.meta["code_boost"] = True
    return g

def build_conversational_rag_graph(query: str) -> RPGGraph:
    g = build_general_rag_graph(query)
    g.meta["domain"] = "conversational"
    for r in g.root_nodes:
        if r.name == "Rerank":
            r.meta["lightweight"] = True
    return g

def configure_rag_for_context(context_type: str, query: str) -> RPGGraph:
    if context_type == "legal":
        return build_legal_rag_graph(query)
    if context_type == "technical":
        return build_technical_rag_graph(query)
    if context_type == "conversational":
        return build_conversational_rag_graph(query)
    return build_general_rag_graph(query)

# -----------------------------
# Plugin system
# -----------------------------
class RAGPlugin(ABC):
    @abstractmethod
    def get_capabilities(self) -> List[str]:
        """Return capabilities offered by the plugin"""
        raise NotImplementedError

    @abstractmethod
    def execute(self, state: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Execute plugin logic and return partial state update"""
        raise NotImplementedError

class LegalRetrievalPlugin(RAGPlugin):
    def get_capabilities(self) -> List[str]:
        return ["legal_document_retrieval", "section_filtering"]

    def execute(self, state: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        hints = dict(state.get("retrieval_hints") or {})
        hints["section_boost"] = True
        hints["k"] = max(12, int(hints.get("k", 10)))
        plugins = list(state.get("plugins") or [])
        if "legal" not in plugins:
            plugins.append("legal")
        return {"retrieval_hints": hints, "plugins": plugins}

# rpg.py (minimal but complete)

from __future__ import annotations

import os
import json
import time
import random
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Tuple, Callable

from policy import need_expand, COVERAGE_TH, DIVERSITY_TH, EPSILON  # thresholds


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


DEFAULT_PATH: List[str] = json.loads(
    os.getenv(
        "RPG_DEFAULT_PATH",
        '["intent_parser","retrieve_rpg","rerank","plan_answer","generate_answer"]',
    )
)


def _prune_meta(meta: Dict[str, Any], max_kv: int = 32) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    for k, v in (meta or {}).items():
        if isinstance(v, (str, int, float, bool)) and len(str(v)) < 500 and len(out) < max_kv:
            out[k] = v
    return out


# ---------------- Feature Tree ----------------

@dataclass(slots=True)
class FeatureTreeNode:
    fid: str
    name: str
    score: float = 0.0
    file_hint: Optional[str] = None
    children: List["FeatureTreeNode"] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "fid": self.fid,
            "name": self.name,
            "score": float(self.score),
            "file_hint": self.file_hint or "",
            "children": [c.to_dict() for c in self.children],
        }


class FeatureTree:
    def __init__(self, roots: Optional[List[FeatureTreeNode]] = None):
        self.roots: List[FeatureTreeNode] = roots or []

    def to_dict(self) -> Dict[str, Any]:
        return {"roots": [r.to_dict() for r in self.roots]}

    def _best_child(self, node: FeatureTreeNode) -> Optional[FeatureTreeNode]:
        if not node.children:
            return None
        return sorted(node.children, key=lambda c: c.score, reverse=True)[0]

    def epsilon_greedy(self, node: FeatureTreeNode, eps: float = 0.1) -> Optional[FeatureTreeNode]:
        if not node.children:
            return None
        if random.random() < max(0.0, min(1.0, eps)):
            return random.choice(node.children)
        return self._best_child(node)


# ---------------- RPG graph ----------------

@dataclass(slots=True)
class RPGNode:
    name: str
    node_type: str  # "capability" | "component" | "function"
    children: List["RPGNode"] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    data_flows: List[Dict[str, Any]] = field(default_factory=list)
    meta: Dict[str, Any] = field(default_factory=dict)  # includes feature_id/file_hint

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
        m = metrics or {}
        path = ["intent_parser", "retrieve_rpg"]
        if need_expand(m):
            path.append("expand_search")
        path += ["rerank", "plan_answer", "generate_answer"]
        return path


# ---------------- Registry & binding ----------------

class RAGComponentRegistry:
    def __init__(self):
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
        self.feature_to_module: Dict[str, str] = {
            "retrieval.semantic": "retrievers/semantic.py",
            "retrieval.hybrid": "retrievers/hybrid.py",
            "retrieval.expand": "retrievers/expand.py",
            "retrieval.legal": "retrievers/legal.py",
            "rerank.cross_encoder": "rerankers/cross_encoder.py",
            "rerank.llm_based": "rerankers/llm_based.py",
            "generator.evidence_based": "generators/evidence.py",
            "generator.template": "generators/template.py",
            "generator.cot": "generators/cot.py",
        }

        if (ov := _load_json_env("RAG_STRATEGIES_JSON")):
            self.retrieval_strategies.update(ov.get("retrieval", {}))
            self.rerankers.update(ov.get("rerankers", {}))
            self.generators.update(ov.get("generators", {}))

        if (ov2 := _load_json_env("FEATURE_TO_MODULE_JSON")):
            self.feature_to_module.update(ov2)

    def merge_feature_hints(self, hints: Dict[str, Any]) -> Dict[str, Any]:
        out = dict(hints or {})
        strat = out.get("strategy", "semantic")
        rer = out.get("reranker", "cross_encoder")
        gen = out.get("generator", "evidence_based")
        features = [f"retrieval.{strat}", f"rerank.{rer}", f"generator.{gen}"]
        file_hints = [self.feature_to_module.get(f) for f in features if f in self.feature_to_module]
        out["feature_ids"] = features
        if file_hints:
            out["file_hints"] = [fh for fh in file_hints if fh]
        return out

    def to_dict(self) -> Dict[str, Any]:
        return {
            "retrieval": self.retrieval_strategies,
            "rerankers": self.rerankers,
            "generators": self.generators,
            "feature_to_module": self.feature_to_module,
        }


def bind_registry_to_hints(registry: Dict[str, Any], context_type: str, base_hints: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
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


# ---------------- Flow & version store (minimal) ----------------

class DataFlowManager:
    def __init__(self):
        self._pre: List[Callable[[str, str, Dict[str, Any]], Dict[str, Any]]] = []
        self._allowed: Dict[Tuple[str, str], bool] = {}

    def add_preprocess(self, fn: Callable[[str, str, Dict[str, Any]], Dict[str, Any]]):
        self._pre.append(fn)

    def preprocess(self, frm: str, to: str, st: Dict[str, Any]) -> Dict[str, Any]:
        out = dict(st or {})
        for fn in self._pre:
            out = fn(frm, to, out) or out
        return out

    def validate(self, frm: str, to: str, snapshot: Dict[str, Any]) -> Dict[str, Any]:
        # 최소 검증: 항상 ok, 필요시 확장
        return {"ok": True, "violations": []}


def merge_rpg(a: Dict[str, Any], b: Dict[str, Any]) -> Dict[str, Any]:
    out = dict(a or {})
    for k, v in (b or {}).items():
        if k not in out:
            out[k] = v
    return out


class RPGVersionStore:
    def __init__(self, root_dir: Optional[str] = None):
        self.root = Path(root_dir or ".rag/versions")
        self.root.mkdir(parents=True, exist_ok=True)
        self._counter = 0

    def save(self, graph: Dict[str, Any], note: str = "") -> int:
        self._counter += 1
        rec = {"version": self._counter, "graph": graph, "ts": time.time(), "note": note}
        path = self.root / f"graph_{self._counter}.json"
        path.write_text(json.dumps(rec, ensure_ascii=False, indent=2), encoding="utf-8")
        return self._counter


def configure_rag_for_context(context_type: str, question: str) -> RPGGraph:
    g = RPGGraph(meta={"context": context_type, "question_len": len(question or "")})
    retr = RPGNode("retrieval", "capability", meta={"context": context_type})
    rer = RPGNode("rerank", "capability")
    gen = RPGNode("generate", "capability")
    g.add_root(retr)
    g.add_root(rer)
    g.add_root(gen)
    return g


def unit_test_flow_assertions(state: Dict[str, Any]) -> Dict[str, Any]:
    # 최소 테스트 훅 (확장 가능)
    return {"ok": True}


# ---------------- Plugin example ----------------

from abc import ABC, abstractmethod

class RAGPlugin(ABC):
    @abstractmethod
    def get_capabilities(self) -> List[str]:
        raise NotImplementedError

    @abstractmethod
    def execute(self, state: Dict[str, Any], **kwargs) -> Dict[str, Any]:
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

# rpg.py (FeatureTree + preprocess/type-guard + version store + merge + ε-greedy)

from __future__ import annotations

import os
import json
import time
import random
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Tuple, Callable, Protocol

from policy import need_expand, COVERAGE_TH, DIVERSITY_TH  # thresholds

# ---------------- Env helpers ----------------
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
    for k, v in meta.items():
        if isinstance(v, (str, int, float, bool)) and len(str(v)) < 500:
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
        # explore with eps, else exploit
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
        # feature -> module/file skeleton hints
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
        # Derive feature keys from hints
        strat = out.get("strategy", "semantic")
        rer = out.get("reranker", "cross_encoder")
        gen = out.get("generator", "evidence_based")
        features = [
            f"retrieval.{strat}",
            f"rerank.{rer}",
            f"generator.{gen}",
        ]
        file_hints = [self.feature_to_module.get(f) for f in features if f in self.feature_to_module]
        # Provide first-class mapping for scaffolding
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

# ---------------- Data flow manager ----------------
class PreprocessFn(Protocol):
    def __call__(self, frm: str, to: str, state: Dict[str, Any]) -> Dict[str, Any]: ...

class DataFlowManager:
    def __init__(self):
        # schema: required keys + expected types
        self.schemas: Dict[Tuple[str, str], Dict[str, Any]] = {
            ("intent_parser", "retrieve_rpg"): {"required": ["refined_query", "retrieval_hints"], "types": {"refined_query": str, "retrieval_hints": dict}},
            ("retrieve_rpg", "award_xp"): {"required": ["retrieved_docs", "retrieval_metrics"], "types": {"retrieved_docs": list, "retrieval_metrics": dict}},
            ("award_xp", "expand_search"): {"required": ["retrieval_metrics"], "types": {"retrieval_metrics": dict}},
            ("award_xp", "rerank"): {"required": ["retrieved_docs"], "types": {"retrieved_docs": list}},
            ("expand_search", "rerank"): {"required": ["retrieved_docs", "retrieval_metrics"], "types": {"retrieved_docs": list, "retrieval_metrics": dict}},
            ("rerank", "plan_answer"): {"required": ["retrieved_docs"], "types": {"retrieved_docs": list}},
            ("plan_answer", "generate_answer"): {"required": ["answer_plan", "retrieved_docs"], "types": {"answer_plan": list, "retrieved_docs": list}},
        }
        self.preprocess_hooks: List[PreprocessFn] = []

    def add_preprocess(self, fn: PreprocessFn) -> None:
        self.preprocess_hooks.append(fn)

    def describe(self) -> List[Dict[str, Any]]:
        return [{"from": frm, "to": to, "schema": sch} for (frm, to), sch in self.schemas.items()]

    def _apply_preprocess(self, frm: str, to: str, state: Dict[str, Any]) -> Dict[str, Any]:
        out = dict(state or {})
        for fn in self.preprocess_hooks:
            try:
                out = fn(frm, to, out) or out
            except Exception:
                # best-effort; ignore faulty hook
                continue
        return out

    def _type_guard(self, types: Dict[str, Any], state: Dict[str, Any]) -> List[str]:
        issues: List[str] = []
        for k, t in (types or {}).items():
            if k in state and state[k] is not None and not isinstance(state[k], t):
                issues.append(f"type({k}) != {getattr(t, '__name__', str(t))}")
        return issues

    def validate(self, frm: str, to: str, state: Dict[str, Any]) -> Dict[str, Any]:
        schema = self.schemas.get((frm, to))
        violations: List[str] = []
        if not schema:
            return {"ok": True, "violations": violations}
        # preprocess before checking
        st = self._apply_preprocess(frm, to, state)
        required = schema.get("required", [])
        for key in required:
            if key not in st or st.get(key) is None:
                violations.append(f"Missing required '{key}' for flow {frm} -> {to}")
        violations += self._type_guard(schema.get("types", {}), st)
        return {"ok": len(violations) == 0, "violations": violations}

def unit_test_flow_assertions(dfm: DataFlowManager) -> List[str]:
    issues: List[str] = []
    for desc in dfm.describe():
        schema = desc["schema"]
        if not isinstance(schema, dict) or "required" not in schema or "types" not in schema:
            issues.append(f"Schema invalid for {desc['from']}->{desc['to']}")
    return issues

# ---------------- Version store & merge ----------------
class RPGVersionStore:
    def __init__(self, root_dir: Optional[str] = None):
        base = root_dir or os.getenv("RPG_STORE_DIR") or ".rag/versions"
        self.root = Path(base).expanduser()
        self.root.mkdir(parents=True, exist_ok=True)

    def _thread_dir(self, thread_id: str) -> Path:
        d = self.root / thread_id
        d.mkdir(parents=True, exist_ok=True)
        return d

    def _load_index(self, thread_id: str) -> Dict[str, Any]:
        idx = self._thread_dir(thread_id) / "index.json"
        if not idx.exists():
            return {"last_version": 0, "records": []}
        try:
            return json.loads(idx.read_text(encoding="utf-8"))
        except Exception:
            return {"last_version": 0, "records": []}

    def _save_index(self, thread_id: str, data: Dict[str, Any]) -> None:
        idx = self._thread_dir(thread_id) / "index.json"
        tmp = idx.with_suffix(".tmp")
        tmp.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        tmp.replace(idx)

    def save_new(self, thread_id: str, payload: Dict[str, Any], note: str = "") -> Dict[str, Any]:
        idx = self._load_index(thread_id)
        ver = int(idx.get("last_version", 0)) + 1
        ts = time.time()
        rec = {"version": ver, "ts": ts, "note": note}
        # persist payload
        (self._thread_dir(thread_id) / f"{ver}.json").write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        idx["last_version"] = ver
        idx["records"] = (idx.get("records") or []) + [rec]
        self._save_index(thread_id, idx)
        return rec

def merge_rpg(prev: Dict[str, Any], new: Dict[str, Any]) -> Dict[str, Any]:
    out = dict(prev or {})
    for k, v in (new or {}).items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            ov = out.get(k, {})
            nv = dict(ov)
            nv.update(v)
            out[k] = nv
        else:
            out[k] = v
    return out

def epsilon_best_strategy(metrics: Dict[str, Any], candidates: List[str], eps: float = 0.15) -> str:
    # Simple heuristic: prefer "expand" if need_expand; else prefer "hybrid" when diversity low; else "semantic"
    if not candidates:
        return "semantic"
    if random.random() < max(0.0, min(1.0, eps)):
        return random.choice(candidates)
    if need_expand(metrics) and "expand" in candidates:
        return "expand"
    diversity = float(metrics.get("diversity") or 0.0)
    if diversity < DIVERSITY_TH and "hybrid" in candidates:
        return "hybrid"
    return candidates[0] if "semantic" not in candidates else "semantic"

# ---------------- Context-specific graph builders ----------------
def build_general_rag_graph(query: str) -> RPGGraph:
    understand = RPGNode("QueryUnderstanding", "capability")
    retrieve = RPGNode("Retrieval", "capability", dependencies=["QueryUnderstanding"])
    rerank = RPGNode("Rerank", "capability", dependencies=["Retrieval"])
    plan = RPGNode("Plan", "capability", dependencies=["Rerank"])
    answer = RPGNode("Answer", "capability", dependencies=["Plan"])

    retrieve_sem = RPGNode("SemanticRetrieval", "component", meta={"k": 8, "feature_id": "retrieval.semantic", "file_hint": "retrievers/semantic.py"})
    retrieve_exp = RPGNode("ExpandedRetrieval", "component", meta={"k": 16, "feature_id": "retrieval.expand", "file_hint": "retrievers/expand.py"})
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

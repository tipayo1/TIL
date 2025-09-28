# rpg.py (lightweight building blocks for LEGO-style agents)
from __future__ import annotations

import os
import re
import json
import time
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Tuple, Callable

# ---------------- Feature Tree (minimal) ----------------
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

# ---------------- RPG graph (placeholder for future) ----------------
@dataclass(slots=True)
class RPGNode:
    name: str
    node_type: str  # "capability" | "component" | "function"
    children: List["RPGNode"] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    data_flows: List[Dict[str, Any]] = field(default_factory=list)
    meta: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "type": self.node_type,
            "dependencies": list(self.dependencies),
            "data_flows": list(self.data_flows),
            "meta": dict(self.meta),
            "children": [c.to_dict() for c in self.children],
        }

@dataclass(slots=True)
class RPGGraph:
    root_nodes: List[RPGNode] = field(default_factory=list)
    meta: Dict[str, Any] = field(default_factory=dict)

    def add_root(self, node: RPGNode) -> None:
        self.root_nodes.append(node)

    def to_dict(self) -> Dict[str, Any]:
        return {"meta": dict(self.meta), "roots": [r.to_dict() for r in self.root_nodes]}

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

# ---------------- Templates (composable) ----------------
@dataclass(slots=True)
class TemplateSpec:
    id: str
    domain: str
    micro_intent: str
    blocks: List[str]

class TemplateRegistry:
    def __init__(self, root: Optional[str] = None):
        self.root = Path(root or os.getenv("TEMPLATE_ROOT", "templates"))
        self.root.mkdir(parents=True, exist_ok=True)
        self._cache: Dict[str, str] = {}

    def load_block(self, block_id: str) -> str:
        if block_id in self._cache:
            return self._cache[block_id]
        path = self.root / f"{block_id}.j2"
        if not path.exists():
            defaults: Dict[str, str] = {
                "common/preamble": "다음 지시를 따르라. 필요한 경우만 간결히 답하라.\n",
                "common/evidence": "요약: {question}\n핵심 근거:\n{evidence}\n",
                "common/sources_tail": "{sources_tail}\n",
                "legal/irac": "이슈: {issue}\n규칙: {rules}\n분석: {analysis}\n결론: {conclusion}\n주의: 본 답변은 일반 정보이며 법률 자문이 아닙니다.\n",
                "technical/rca": "현상: {symptom}\n재현: {repro}\n원인: {cause}\n수정: {fix}\n검증: {verify}\n",
                "conversational/ack_ask_act": "공감: {ack}\n질문: {ask}\n제안: {act}\n",
            }
            text = defaults.get(block_id, f"[{block_id}]")
            self._cache[block_id] = text
            return text
        txt = path.read_text(encoding="utf-8")
        self._cache[block_id] = txt
        return txt

    def compose(self, spec: TemplateSpec) -> str:
        return "\n\n".join(self.load_block(b) for b in spec.blocks)

    def to_dict(self) -> Dict[str, Any]:
        return {"root": str(self.root)}

# ---------------- Ontology (lightweight) ----------------
class OntologyProvider:
    def __init__(self, path: Optional[str] = None, json_env: Optional[str] = "ONTOLOGY_JSON"):
        self.path = Path(path or os.getenv("ONTOLOGY_PATH", "ontology.yaml"))
        self._raw: Dict[str, Any] = {}
        env_data = None
        try:
            env_data = json.loads(os.getenv(json_env) or "{}")
        except Exception:
            env_data = {}
        if env_data:
            self._raw = env_data
        else:
            if self.path.exists():
                text = self.path.read_text(encoding="utf-8")
                if self.path.suffix.lower() in (".json",):
                    try:
                        self._raw = json.loads(text)
                    except Exception:
                        self._raw = {}
                else:
                    try:
                        import yaml  # type: ignore
                        self._raw = yaml.safe_load(text) or {}
                    except Exception:
                        self._raw = {}
        if not isinstance(self._raw, dict):
            self._raw = {}

    @property
    def version(self) -> str:
        raw = self._raw if isinstance(self._raw, dict) else {}
        return str(raw.get("version") or raw.get("_v") or "v0")

    def enrich(self, q: str, base_hints: Dict[str, Any]) -> Dict[str, Any]:
        hints = dict(base_hints or {})
        ql = (q or "").lower()
        must_terms: List[str] = list(hints.get("must_terms") or [])
        filters: Dict[str, Any] = {}
        tpl_hints: Dict[str, Any] = {}

        concepts = (self._raw.get("concepts") or {}) if isinstance(self._raw, dict) else {}
        for _, c in concepts.items():
            syns = [str(s).lower() for s in (c.get("synonyms") or [])]

            def match(s: str) -> bool:
                return bool(re.search(s[3:], ql)) if s.startswith("re:") else s in ql

            if any(match(s) for s in syns):
                must_terms += list(c.get("must_terms") or [])
                for k, v in (c.get("filters") or {}).items():
                    filters[k] = v
                for k, v in (c.get("template_hints") or {}).items():
                    tpl_hints[k] = v

        if must_terms:
            hints["must_terms"] = sorted(set(must_terms))
        hints.update(filters)
        hints.update(tpl_hints)
        hints["ontology_version"] = self.version
        return hints

    def to_dict(self) -> Dict[str, Any]:
        return {"version": self.version}

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
        try:
            ov = json.loads(os.getenv("RAG_STRATEGIES_JSON") or "{}")
            self.retrieval_strategies.update(ov.get("retrieval", {}))
            self.rerankers.update(ov.get("rerankers", {}))
            self.generators.update(ov.get("generators", {}))
        except Exception:
            pass
        try:
            ov2 = json.loads(os.getenv("FEATURE_TO_MODULE_JSON") or "{}")
            if isinstance(ov2, dict):
                self.feature_to_module.update(ov2)
        except Exception:
            pass

    def to_dict(self) -> Dict[str, Any]:
        return {
            "retrieval": self.retrieval_strategies,
            "rerankers": self.rerankers,
            "generators": self.generators,
            "feature_to_module": self.feature_to_module,
        }

def bind_registry_to_hints(registry: Dict[str, Any], context_type: str, base_hints: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    hints = dict(base_hints or {})
    retr_map = registry.get("retrieval", {}) if isinstance(registry, dict) else {}
    rer_map = registry.get("rerankers", {}) if isinstance(registry, dict) else {}
    gen_map = registry.get("generators", {}) if isinstance(registry, dict) else {}

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

# ---------------- Flow & tests (stubs) ----------------
class DataFlowManager:
    def __init__(self):
        self._pre: List[Callable[[str, str, Dict[str, Any]], Dict[str, Any]]] = []

    def add_preprocess(self, fn: Callable[[str, str, Dict[str, Any]], Dict[str, Any]]):
        self._pre.append(fn)

    def preprocess(self, frm: str, to: str, st: Dict[str, Any]) -> Dict[str, Any]:
        out = dict(st or {})
        for fn in self._pre:
            out = fn(frm, to, out) or out
        return out

def unit_test_flow_assertions(state_or_graph: Dict[str, Any]) -> Dict[str, Any]:
    return {"ok": True}

# ---------------- Context configurator ----------------
def configure_rag_for_context(context_type: str) -> Tuple[RAGComponentRegistry, TemplateRegistry, OntologyProvider]:
    reg = RAGComponentRegistry()
    tpl = TemplateRegistry()
    onto = OntologyProvider()
    return reg, tpl, onto

# rpg.py
# - RPG-Lite: 레지스트리(전략)·템플릿·온톨로지·툴 플러그인
# - 실행 경로에서 쓰는 최소 필드만 유지

from __future__ import annotations

import os
import re
import importlib
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Callable

# ---------------- Feature Tree (경량 프로필) ----------------

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

# ---------------- Registry ----------------

class RAGComponentRegistry:
    """
    검색/리랭크/생성 전략을 주입식으로 관리하는 레지스트리.
    - 서비스/도메인별 JSON 오버라이드로 무중단 교체 가능
    """
    def __init__(self):
        self.retrievers: Dict[str, Dict[str, Any]] = {
            "semantic": {"k": 6, "weight": 1.0},
            "hybrid": {"k": 8, "weight_dense": 0.7, "weight_sparse": 0.3},
            "expand": {"k": 12, "diversity_boost": True},
        }
        # reranker: 기본 overlap, 경량 CE 옵션(lite_ce) + 환경변수 모델 토글
        self.rerankers: Dict[str, Dict[str, Any]] = {
            "none": {"type": "none"},
            "overlap": {"type": "overlap"},
            "lite_ce": {
                "type": "cross_encoder",
                "model": os.getenv("RERANK_CE_MODEL", "cross-encoder/ms-marco-MiniLM-L-6-v2"),
                "batch_size": int(os.getenv("RERANK_CE_BATCH_SIZE", "16")),
                "topn": int(os.getenv("RERANK_TOPN", "10")),
            },
        }
        self.generators: Dict[str, Dict[str, Any]] = {
            "default": {"style": "concise", "citations": True},
        }

    def snapshot(self) -> Dict[str, Any]:
        return {
            "retrievers": self.retrievers,
            "rerankers": self.rerankers,
            "generators": self.generators,
        }

class TemplateRegistry:
    """
    프롬프트 템플릿 블록 조합.
    - 최소 공통 블록만 유지 (표면 축소)
    """
    def __init__(self):
        self.blocks: Dict[str, str] = {
            "system_base": "You are a helpful assistant. Answer with evidence when available.",
            "ask_intent": "Rewrite the query for retrieval. Keep core intent and constraints.",
            "plan_answer": "Break the answer into 2-4 claims and map evidence indices.",
            "generate_answer": "Write a direct answer. If citations are provided, include them.",
        }

    def get(self, key: str) -> str:
        return self.blocks.get(key, "")

# ---------------- Ontology ----------------

class OntologyProvider:
    """
    간단한 질의 분석으로 must_terms/filters/entities/도메인 힌트 생성.
    - HR 미니 스키마
    - Relation은 필터 수준에서 year/section/domain만 경량 반영
    """
    HR_SYNONYMS: Dict[str, List[str]] = {
        "Policy": ["policy", "규정", "지침", "내규"],
        "Role": ["role", "직무", "직책", "역할"],
        "Employee": ["employee", "사원", "직원", "근로자"],
        "Department": ["department", "부서", "팀"],
        "Document": ["document", "문서", "자료"],
        "Contract": ["contract", "계약", "근로계약"],
        "Recruiting": ["recruit", "채용", "모집"],
        "Leave": ["leave", "휴가", "휴직"],
        "Compensation": ["compensation", "연봉", "보상", "급여", "임금"],
        "Performance": ["performance", "성과", "평가"],
    }

    def analyze(self, query: str) -> Dict[str, Any]:
        must_terms: List[str] = []
        filters: Dict[str, Any] = {}
        entities: List[str] = []
        ql = (query or "").lower()

        # 연도
        years = re.findall(r"(20\d{2})", query or "")
        if years:
            filters["year"] = max(years)

        # 섹션/도메인 추정
        if any(w in ql for w in ["policy", "규정", "지침", "내규"]):
            filters["section"] = "policy"
        if any(w in ql for w in ["hr", "인사", "채용", "보상", "휴가", "평가"]):
            filters["domain"] = "hr"

        # 엔티티/개념 매칭
        for ent, syns in self.HR_SYNONYMS.items():
            if any(s.lower() in ql for s in syns):
                entities.append(ent)

        # 핵심 단어를 must로 (최대 5개)
        tokens = [t for t in re.split(r"[^a-zA-Z0-9가-힣]+", query or "") if len(t) >= 2]
        if tokens:
            must_terms.extend(tokens[:5])

        return {
            "must_terms": must_terms,
            "filters": filters,
            "entities": sorted(list(set(entities))),
            "ontology_version": "hr-lite-v0.2",
            "domain": filters.get("domain", "general"),
        }

# ---------------- Registry ↔ Hints 바인딩 ----------------

def bind_registry_to_hints(registry: RAGComponentRegistry, hints: Dict[str, Any]) -> Dict[str, Any]:
    """
    레지스트리 기본값을 hints에 병합(기존 hints 우선).
    """
    merged = dict(hints or {})
    # 최소 기본 전략
    merged.setdefault("strategy", "hybrid")
    strat = merged["strategy"]
    merged.setdefault("params", dict(registry.retrievers.get(strat, {"k": 8})))
    # rerank 기본
    merged.setdefault("rerank", "overlap")
    merged.setdefault("rerank_params", dict(registry.rerankers.get(merged["rerank"], {"type": "overlap"})))
    # generator 기본
    merged.setdefault("generator", "default")
    merged.setdefault("generator_params", dict(registry.generators.get("default", {})))
    # 온톨로지 힌트 직렬 반영
    merged.setdefault("filters", hints.get("filters", {}))
    merged.setdefault("must_terms", hints.get("must_terms", []))
    return merged

# ---------------- Prompt 유틸 ----------------

def get_prompt(templ: TemplateRegistry, key: str) -> str:
    return templ.get(key)

# ---------------- Tool Plugins ----------------

def _load_tool(mod_name: str, func: str) -> Optional[Callable]:
    try:
        mod = importlib.import_module(mod_name)
        return getattr(mod, func)
    except Exception:
        return None

def call_tool(tool_spec: Dict[str, str], **kwargs) -> Any:
    """
    동적 로딩 기반 경량 툴 호출.
    - {"module": "pkg.mod", "func": "fn"}
    """
    fn = _load_tool(tool_spec.get("module", ""), tool_spec.get("func", ""))
    if not fn:
        return None
    return fn(**kwargs)

def suggest_tools_for_context(context: Dict[str, Any]) -> List[Dict[str, str]]:
    """
    매우 단순한 컨텍스트 기반 툴 제안.
    """
    tools: List[Dict[str, str]] = []
    if context.get("need_citation"):
        tools.append({"module": "utils.citation", "func": "citation_check"})
    return tools

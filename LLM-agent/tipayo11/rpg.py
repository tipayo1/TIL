"""
rpg.py - Repository Planning Graph 관리 모듈

RPG(Repository Planning Graph)를 구현한 모듈로서 논문의 핵심 개념을 경량화하여 적용:
- 제안 레벨과 구현 레벨의 통합 계획
- 기능적 계층구조와 데이터 플로우 관리  
- 동적 워크플로우 및 의사결정 지원
- Human-in-the-Loop 대체를 위한 자동화된 계획 수립
"""

import json
import logging
from typing import Dict, List, Optional, Set, Tuple, Any, Union
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod
import networkx as nx
from datetime import datetime


class NodeType(Enum):
    """RPG 노드 타입 정의"""
    FUNCTIONAL = "functional"      # 기능적 노드
    IMPLEMENTATION = "implementation"  # 구현 노드
    DATA_FLOW = "data_flow"       # 데이터 플로우 노드
    DECISION = "decision"         # 의사결정 노드


class EdgeType(Enum):
    """RPG 엣지 타입 정의"""
    HIERARCHICAL = "hierarchical"     # 계층적 관계
    DATA_FLOW = "data_flow"          # 데이터 흐름
    DEPENDENCY = "dependency"        # 의존성
    EXECUTION_ORDER = "execution"    # 실행 순서


@dataclass
class RPGNode:
    """RPG 노드 클래스"""
    id: str
    name: str
    node_type: NodeType
    description: str = ""
    properties: Dict[str, Any] = field(default_factory=dict)
    capabilities: List[str] = field(default_factory=list)
    requirements: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass 
class RPGEdge:
    """RPG 엣지 클래스"""
    source: str
    target: str
    edge_type: EdgeType
    weight: float = 1.0
    properties: Dict[str, Any] = field(default_factory=dict)


class RPGBuilder(ABC):
    """RPG 구축을 위한 추상 빌더 클래스"""

    @abstractmethod
    def build_functional_hierarchy(self, domain: str, user_intent: str) -> List[RPGNode]:
        """기능적 계층구조 구축"""
        pass

    @abstractmethod
    def build_implementation_mapping(self, functional_nodes: List[RPGNode]) -> List[RPGNode]:
        """구현 레벨 매핑"""
        pass

    @abstractmethod
    def build_data_flow(self, nodes: List[RPGNode]) -> List[RPGEdge]:
        """데이터 플로우 구축"""
        pass


class DomainAdaptiveRPGBuilder(RPGBuilder):
    """도메인 적응적 RPG 빌더 - 다양한 도메인에 동적 적응"""

    def __init__(self, domain_config: Optional[Dict] = None):
        self.domain_config = domain_config or {}
        self.logger = logging.getLogger(__name__)

    def build_functional_hierarchy(self, domain: str, user_intent: str) -> List[RPGNode]:
        """사용자 의도를 기반으로 기능적 계층구조를 동적으로 구축"""
        nodes = []

        # 도메인별 기본 기능 노드들
        base_functions = self._get_base_functions_for_domain(domain)

        # 사용자 의도를 파싱하여 필요한 기능들 식별
        required_functions = self._parse_user_intent(user_intent)

        # 기능 노드 생성
        for func_name, func_info in {**base_functions, **required_functions}.items():
            node = RPGNode(
                id=f"func_{func_name}",
                name=func_name,
                node_type=NodeType.FUNCTIONAL,
                description=func_info.get("description", ""),
                capabilities=func_info.get("capabilities", []),
                requirements=func_info.get("requirements", [])
            )
            nodes.append(node)

        return nodes

    def build_implementation_mapping(self, functional_nodes: List[RPGNode]) -> List[RPGNode]:
        """기능 노드들을 구체적인 구현 노드로 매핑"""
        impl_nodes = []

        for func_node in functional_nodes:
            # 기능을 구현할 수 있는 구체적인 노드들 생성
            implementations = self._generate_implementations(func_node)
            impl_nodes.extend(implementations)

        return impl_nodes

    def build_data_flow(self, nodes: List[RPGNode]) -> List[RPGEdge]:
        """노드들 간의 데이터 플로우 관계 구축"""
        edges = []

        # 노드들 간의 의존성 분석
        for source_node in nodes:
            for target_node in nodes:
                if source_node.id != target_node.id:
                    dependency = self._analyze_dependency(source_node, target_node)
                    if dependency:
                        edge = RPGEdge(
                            source=source_node.id,
                            target=target_node.id,
                            edge_type=dependency["type"],
                            weight=dependency["weight"],
                            properties=dependency.get("properties", {})
                        )
                        edges.append(edge)

        return edges

    def _get_base_functions_for_domain(self, domain: str) -> Dict[str, Dict]:
        """도메인별 기본 기능들을 반환"""
        domain_functions = {
            "hr": {
                "question_analysis": {
                    "description": "HR 질문 분석 및 분류",
                    "capabilities": ["intent_recognition", "entity_extraction"],
                    "requirements": ["nlp_model"]
                },
                "document_retrieval": {
                    "description": "관련 문서 검색 및 추출",
                    "capabilities": ["semantic_search", "ranking"],
                    "requirements": ["vector_db", "embedding_model"]
                },
                "answer_generation": {
                    "description": "답변 생성 및 검증",
                    "capabilities": ["text_generation", "fact_checking"],
                    "requirements": ["llm_model", "validation_rules"]
                }
            }
        }
        return domain_functions.get(domain, {})

    def _parse_user_intent(self, user_intent: str) -> Dict[str, Dict]:
        """사용자 의도를 파싱하여 필요한 기능들을 식별 (실제로는 LLM 활용)"""
        # 간단한 키워드 기반 예시 (실제로는 더 정교한 LLM 기반 파싱)
        parsed_functions = {}

        if "검색" in user_intent or "찾기" in user_intent:
            parsed_functions["enhanced_search"] = {
                "description": "향상된 검색 기능",
                "capabilities": ["multi_modal_search", "context_aware"],
                "requirements": ["advanced_retrieval"]
            }

        if "분석" in user_intent or "요약" in user_intent:
            parsed_functions["content_analysis"] = {
                "description": "콘텐츠 분석 및 요약",
                "capabilities": ["summarization", "key_extraction"],
                "requirements": ["analysis_model"]
            }

        return parsed_functions

    def _generate_implementations(self, func_node: RPGNode) -> List[RPGNode]:
        """기능 노드를 위한 구현 노드들 생성"""
        implementations = []

        # 기능에 따른 구현 방식들
        if "search" in func_node.name.lower():
            implementations.extend([
                RPGNode(
                    id=f"impl_vector_search_{func_node.id}",
                    name="Vector Search Implementation",
                    node_type=NodeType.IMPLEMENTATION,
                    description="벡터 기반 의미 검색 구현",
                    properties={"method": "vector", "backend": "configurable"}
                ),
                RPGNode(
                    id=f"impl_hybrid_search_{func_node.id}",
                    name="Hybrid Search Implementation", 
                    node_type=NodeType.IMPLEMENTATION,
                    description="하이브리드 검색 (벡터 + 키워드) 구현",
                    properties={"method": "hybrid", "components": ["vector", "bm25"]}
                )
            ])

        if "analysis" in func_node.name.lower():
            implementations.append(
                RPGNode(
                    id=f"impl_llm_analysis_{func_node.id}",
                    name="LLM Analysis Implementation",
                    node_type=NodeType.IMPLEMENTATION,
                    description="LLM 기반 분석 구현",
                    properties={"model_type": "configurable", "provider": "multi"}
                )
            )

        return implementations

    def _analyze_dependency(self, source: RPGNode, target: RPGNode) -> Optional[Dict]:
        """두 노드 간의 의존성 관계 분석"""
        # 간단한 규칙 기반 의존성 분석
        dependencies = []

        # 데이터 플로우 의존성
        if any(req in source.capabilities for req in target.requirements):
            return {
                "type": EdgeType.DATA_FLOW,
                "weight": 0.8,
                "properties": {"flow_type": "data"}
            }

        # 실행 순서 의존성 
        if source.node_type == NodeType.FUNCTIONAL and target.node_type == NodeType.IMPLEMENTATION:
            if source.id.replace("func_", "") in target.id:
                return {
                    "type": EdgeType.DEPENDENCY,
                    "weight": 1.0,
                    "properties": {"dep_type": "implements"}
                }

        return None


class RepositoryPlanningGraph:
    """Repository Planning Graph 메인 클래스"""

    def __init__(self, builder: Optional[RPGBuilder] = None):
        self.builder = builder or DomainAdaptiveRPGBuilder()
        self.graph = nx.DiGraph()
        self.nodes: Dict[str, RPGNode] = {}
        self.edges: Dict[str, RPGEdge] = {}
        self.metadata = {
            "created_at": datetime.now(),
            "domain": None,
            "user_intent": None
        }
        self.logger = logging.getLogger(__name__)

    def construct_from_intent(self, domain: str, user_intent: str) -> 'RepositoryPlanningGraph':
        """사용자 의도를 기반으로 RPG 구축"""
        self.metadata["domain"] = domain
        self.metadata["user_intent"] = user_intent

        # 1단계: 기능적 계층구조 구축
        functional_nodes = self.builder.build_functional_hierarchy(domain, user_intent)

        # 2단계: 구현 레벨 매핑
        impl_nodes = self.builder.build_implementation_mapping(functional_nodes)

        # 3단계: 모든 노드 통합
        all_nodes = functional_nodes + impl_nodes
        for node in all_nodes:
            self.add_node(node)

        # 4단계: 데이터 플로우 구축
        edges = self.builder.build_data_flow(all_nodes)
        for edge in edges:
            self.add_edge(edge)

        self.logger.info(f"RPG 구축 완료: {len(self.nodes)} 노드, {len(self.edges)} 엣지")
        return self

    def add_node(self, node: RPGNode):
        """노드 추가"""
        self.nodes[node.id] = node
        self.graph.add_node(node.id, **node.__dict__)

    def add_edge(self, edge: RPGEdge):
        """엣지 추가"""
        edge_id = f"{edge.source}->{edge.target}"
        self.edges[edge_id] = edge
        self.graph.add_edge(edge.source, edge.target, **edge.__dict__)

    def get_execution_order(self) -> List[str]:
        """토폴로지 정렬을 통한 실행 순서 반환"""
        try:
            return list(nx.topological_sort(self.graph))
        except nx.NetworkXError:
            # 순환 참조가 있는 경우 간단한 휴리스틱 사용
            self.logger.warning("순환 참조 감지, 휴리스틱 순서 반환")
            return list(self.nodes.keys())

    def get_node_dependencies(self, node_id: str) -> List[str]:
        """특정 노드의 의존성 반환"""
        return list(self.graph.predecessors(node_id))

    def get_context_for_node(self, node_id: str) -> Dict[str, Any]:
        """특정 노드의 컨텍스트 정보 반환"""
        if node_id not in self.nodes:
            return {}

        node = self.nodes[node_id]
        dependencies = self.get_node_dependencies(node_id)

        context = {
            "node": node.__dict__,
            "dependencies": [self.nodes[dep_id].__dict__ for dep_id in dependencies],
            "execution_ready": self._is_execution_ready(node_id),
            "suggested_tools": self._suggest_tools_for_node(node)
        }

        return context

    def _is_execution_ready(self, node_id: str) -> bool:
        """노드가 실행 준비되었는지 확인"""
        dependencies = self.get_node_dependencies(node_id)
        # 실제로는 더 복잡한 준비 상태 검증 로직
        return len(dependencies) == 0  # 간단한 예시

    def _suggest_tools_for_node(self, node: RPGNode) -> List[str]:
        """노드에 적합한 도구들 제안"""
        tools = []

        if "search" in node.name.lower():
            tools.extend(["vector_retriever", "bm25_retriever", "hybrid_retriever"])

        if "analysis" in node.name.lower():
            tools.extend(["llm_analyzer", "summarizer", "entity_extractor"])

        if node.node_type == NodeType.IMPLEMENTATION:
            tools.append("code_generator")

        return tools

    def update_node_status(self, node_id: str, status: str, results: Any = None):
        """노드 실행 상태 업데이트"""
        if node_id in self.nodes:
            self.nodes[node_id].properties["status"] = status
            self.nodes[node_id].properties["last_updated"] = datetime.now()
            if results:
                self.nodes[node_id].properties["results"] = results

    def to_dict(self) -> Dict[str, Any]:
        """RPG를 딕셔너리로 직렬화"""
        return {
            "metadata": self.metadata,
            "nodes": {node_id: node.__dict__ for node_id, node in self.nodes.items()},
            "edges": {edge_id: edge.__dict__ for edge_id, edge in self.edges.items()},
            "execution_order": self.get_execution_order()
        }

    def from_dict(self, data: Dict[str, Any]) -> 'RepositoryPlanningGraph':
        """딕셔너리에서 RPG 복원"""
        self.metadata = data["metadata"]

        # 노드 복원
        for node_data in data["nodes"].values():
            node = RPGNode(**node_data)
            self.add_node(node)

        # 엣지 복원
        for edge_data in data["edges"].values():
            edge = RPGEdge(**edge_data)
            self.add_edge(edge)

        return self


# 유틸리티 함수들
def create_hr_rpg(user_question: str) -> RepositoryPlanningGraph:
    """HR 도메인용 RPG 생성"""
    builder = DomainAdaptiveRPGBuilder()
    rpg = RepositoryPlanningGraph(builder)
    return rpg.construct_from_intent("hr", user_question)


def get_next_executable_nodes(rpg: RepositoryPlanningGraph) -> List[str]:
    """다음 실행 가능한 노드들 반환"""
    execution_order = rpg.get_execution_order()

    for node_id in execution_order:
        if rpg._is_execution_ready(node_id):
            node_status = rpg.nodes[node_id].properties.get("status")
            if node_status != "completed":
                return [node_id]

    return []

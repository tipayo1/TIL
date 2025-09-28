# 2. rpg.py - Repository Planning Graph 관리
code_structure["rpg.py"] = '''
# rpg.py - Repository Planning Graph (RPG) 시스템
# 논문의 RPG 로직을 경량화하여 RAG에 적용

from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import networkx as nx
import json
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class NodeType(Enum):
    """RPG 노드 타입"""
    CAPABILITY = "capability"    # 기능 노드 (사용자 요구사항)
    FILE = "file"               # 파일 노드 (문서, 코드)
    FUNCTION = "function"       # 함수 노드 (처리 로직)
    DEPENDENCY = "dependency"   # 의존성 노드 (전제 조건)
    DATA_FLOW = "data_flow"     # 데이터 흐름 노드

class ExecutionPhase(Enum):
    """실행 단계"""
    PLANNING = "planning"
    REFINEMENT = "refinement" 
    EXECUTION = "execution"
    VALIDATION = "validation"

@dataclass
class RPGNode:
    """RPG 노드 클래스"""
    node_id: str
    node_type: NodeType
    name: str
    description: str
    status: str = "planned"  # planned, active, completed, failed
    metadata: Dict[str, Any] = field(default_factory=dict)
    inputs: List[str] = field(default_factory=list)
    outputs: List[str] = field(default_factory=list)
    priority: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return {
            "node_id": self.node_id,
            "node_type": self.node_type.value,
            "name": self.name,
            "description": self.description,
            "status": self.status,
            "metadata": self.metadata,
            "inputs": self.inputs,
            "outputs": self.outputs,
            "priority": self.priority
        }

class RPGGraph:
    """RPG 그래프 관리 클래스"""
    
    def __init__(self):
        self.graph = nx.DiGraph()  # 방향성 그래프
        self.nodes: Dict[str, RPGNode] = {}
        self.execution_plan: List[str] = []
        self.current_phase = ExecutionPhase.PLANNING
        
    def add_node(self, node: RPGNode) -> None:
        """노드 추가"""
        self.nodes[node.node_id] = node
        self.graph.add_node(node.node_id, **node.to_dict())
        logger.info(f"RPG 노드 추가: {node.node_id} ({node.node_type.value})")
    
    def add_edge(self, from_node: str, to_node: str, 
                 edge_type: str = "dependency") -> None:
        """엣지 추가 (의존성 관계)"""
        if from_node in self.nodes and to_node in self.nodes:
            self.graph.add_edge(from_node, to_node, edge_type=edge_type)
            logger.info(f"RPG 엣지 추가: {from_node} -> {to_node} ({edge_type})")
    
    def get_execution_order(self) -> List[str]:
        """위상 정렬을 통한 실행 순서 결정"""
        try:
            self.execution_plan = list(nx.topological_sort(self.graph))
            return self.execution_plan
        except nx.NetworkXError:
            logger.error("순환 의존성 발견, 실행 순서 결정 실패")
            return []
    
    def get_ready_nodes(self) -> List[str]:
        """실행 가능한 노드들 반환 (의존성이 완료된 노드)"""
        ready_nodes = []
        for node_id, node in self.nodes.items():
            if node.status == "planned":
                # 모든 의존성이 완료되었는지 확인
                dependencies = list(self.graph.predecessors(node_id))
                if all(self.nodes[dep].status == "completed" for dep in dependencies):
                    ready_nodes.append(node_id)
        return ready_nodes
    
    def update_node_status(self, node_id: str, status: str, 
                          metadata: Optional[Dict[str, Any]] = None) -> None:
        """노드 상태 업데이트"""
        if node_id in self.nodes:
            self.nodes[node_id].status = status
            if metadata:
                self.nodes[node_id].metadata.update(metadata)
            logger.info(f"노드 상태 업데이트: {node_id} -> {status}")

class RPGPlanner:
    """RPG 계획 수립 클래스"""
    
    def __init__(self, llm_agent=None):
        self.llm_agent = llm_agent
    
    def create_capability_graph(self, user_request: str, 
                               domain_context: str = "") -> RPGGraph:
        """
        사용자 요청으로부터 능력 그래프 생성
        논문의 proposal-level planning 구현
        """
        rpg = RPGGraph()
        
        # 1. 주요 기능 추출
        capabilities = self._extract_capabilities(user_request, domain_context)
        
        # 2. 기능 노드 생성
        for i, cap in enumerate(capabilities):
            node = RPGNode(
                node_id=f"cap_{i}",
                node_type=NodeType.CAPABILITY,
                name=cap["name"],
                description=cap["description"],
                priority=cap.get("priority", 0),
                metadata={"domain": domain_context, "user_request": user_request}
            )
            rpg.add_node(node)
        
        # 3. 의존성 관계 설정
        self._establish_dependencies(rpg, capabilities)
        
        return rpg
    
    def refine_to_implementation(self, rpg: RPGGraph) -> RPGGraph:
        """
        기능 그래프를 구현 수준으로 정제
        논문의 implementation-level refinement 구현
        """
        # 각 기능 노드를 실제 처리 노드로 분해
        for node_id, node in list(rpg.nodes.items()):
            if node.node_type == NodeType.CAPABILITY:
                impl_nodes = self._decompose_capability(node)
                
                # 구현 노드들 추가
                for impl_node in impl_nodes:
                    rpg.add_node(impl_node)
                    rpg.add_edge(node_id, impl_node.node_id, "implements")
        
        # 실행 순서 재계산
        rpg.get_execution_order()
        
        return rpg
    
    def _extract_capabilities(self, user_request: str, 
                             domain_context: str) -> List[Dict[str, Any]]:
        """LLM을 통한 기능 추출"""
        if not self.llm_agent:
            # 기본 규칙 기반 분석
            return [
                {"name": "질문_분석", "description": "사용자 질문 분석 및 정제", "priority": 1},
                {"name": "정보_검색", "description": "관련 문서 검색 및 수집", "priority": 2}, 
                {"name": "답변_생성", "description": "검색된 정보 기반 답변 생성", "priority": 3},
                {"name": "품질_검증", "description": "답변 품질 검증 및 개선", "priority": 4}
            ]
        
        # LLM 기반 기능 분석 (향후 구현)
        prompt = f"""
        사용자 요청: {user_request}
        도메인 컨텍스트: {domain_context}
        
        이 요청을 처리하기 위한 주요 기능들을 JSON 형태로 추출해주세요.
        각 기능은 name, description, priority를 포함해야 합니다.
        """
        
        # LLM 호출 로직 (생략)
        return []
    
    def _establish_dependencies(self, rpg: RPGGraph, 
                               capabilities: List[Dict[str, Any]]) -> None:
        """기능 간 의존성 관계 설정"""
        # 간단한 순차 의존성 설정 (실제로는 더 복잡한 로직 필요)
        sorted_caps = sorted(capabilities, key=lambda x: x.get("priority", 0))
        for i in range(1, len(sorted_caps)):
            rpg.add_edge(f"cap_{i-1}", f"cap_{i}", "sequential")
    
    def _decompose_capability(self, capability_node: RPGNode) -> List[RPGNode]:
        """기능 노드를 구현 노드들로 분해"""
        # 기능별 구현 노드 생성 로직
        impl_nodes = []
        
        if "질문_분석" in capability_node.name:
            impl_nodes = [
                RPGNode(f"{capability_node.node_id}_preprocess", 
                       NodeType.FUNCTION, "질문 전처리", "질문 정제 및 표준화"),
                RPGNode(f"{capability_node.node_id}_classify", 
                       NodeType.FUNCTION, "의도 분류", "질문 의도 및 카테고리 분류")
            ]
        elif "정보_검색" in capability_node.name:
            impl_nodes = [
                RPGNode(f"{capability_node.node_id}_retrieve", 
                       NodeType.FUNCTION, "문서 검색", "벡터 DB 검색"),
                RPGNode(f"{capability_node.node_id}_rerank", 
                       NodeType.FUNCTION, "재순위화", "검색 결과 재순위화")
            ]
        
        return impl_nodes

class RPGExecutor:
    """RPG 실행 관리 클래스"""
    
    def __init__(self, rpg: RPGGraph):
        self.rpg = rpg
        self.execution_context = {}
    
    def execute_next_ready_node(self, state_manager) -> Optional[str]:
        """다음 실행 가능한 노드 실행"""
        ready_nodes = self.rpg.get_ready_nodes()
        
        if not ready_nodes:
            return None
            
        # 우선순위가 높은 노드 선택
        next_node_id = max(ready_nodes, 
                          key=lambda x: self.rpg.nodes[x].priority)
        
        # 노드 실행
        return self._execute_node(next_node_id, state_manager)
    
    def _execute_node(self, node_id: str, state_manager) -> str:
        """개별 노드 실행"""
        node = self.rpg.nodes[node_id]
        logger.info(f"RPG 노드 실행 시작: {node_id}")
        
        # 노드 상태를 active로 변경
        self.rpg.update_node_status(node_id, "active")
        
        try:
            if node.node_type == NodeType.FUNCTION:
                result = self._execute_function_node(node, state_manager)
            elif node.node_type == NodeType.CAPABILITY:
                result = self._execute_capability_node(node, state_manager)
            else:
                result = f"노드 타입 {node.node_type} 실행 완료"
            
            # 성공시 completed 상태로 변경
            self.rpg.update_node_status(node_id, "completed", 
                                       {"result": result})
            return result
            
        except Exception as e:
            # 실패시 failed 상태로 변경
            self.rpg.update_node_status(node_id, "failed", 
                                       {"error": str(e)})
            logger.error(f"노드 실행 실패: {node_id} - {str(e)}")
            return f"실행 실패: {str(e)}"
    
    def _execute_function_node(self, node: RPGNode, state_manager) -> str:
        """함수 노드 실행"""
        # 실제 함수 매핑 및 실행 로직
        if "전처리" in node.name:
            # 질문 전처리 실행
            return "질문 전처리 완료"
        elif "검색" in node.name:
            # 문서 검색 실행
            return "문서 검색 완료"
        # ... 기타 함수들
        
        return f"{node.name} 실행 완료"
    
    def _execute_capability_node(self, node: RPGNode, state_manager) -> str:
        """능력 노드 실행 (추상적 능력 실행)"""
        return f"능력 {node.name} 실행 완료"
'''

print("=== rpg.py 구조 ===")
print(code_structure["rpg.py"][:2000] + "...")
print(f"전체 길이: {len(code_structure['rpg.py'])} characters")
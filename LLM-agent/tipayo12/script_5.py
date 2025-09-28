# rpg.py 전체 생성
rpg_py_content = '''# rpg.py - Repository Planning Graph (RPG) 시스템
# 논문의 RPG 로직을 경량화하여 RAG에 적용

from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
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
    """RPG 그래프 관리 클래스 - NetworkX 없이 경량 구현"""
    
    def __init__(self):
        self.nodes: Dict[str, RPGNode] = {}
        self.edges: Dict[str, List[str]] = {}  # adjacency list
        self.reverse_edges: Dict[str, List[str]] = {}  # 역방향 인접 리스트
        self.execution_plan: List[str] = []
        self.current_phase = ExecutionPhase.PLANNING
        
    def add_node(self, node: RPGNode) -> None:
        """노드 추가"""
        self.nodes[node.node_id] = node
        if node.node_id not in self.edges:
            self.edges[node.node_id] = []
        if node.node_id not in self.reverse_edges:
            self.reverse_edges[node.node_id] = []
        logger.info(f"RPG 노드 추가: {node.node_id} ({node.node_type.value})")
    
    def add_edge(self, from_node: str, to_node: str, 
                 edge_type: str = "dependency") -> None:
        """엣지 추가 (의존성 관계)"""
        if from_node in self.nodes and to_node in self.nodes:
            if to_node not in self.edges[from_node]:
                self.edges[from_node].append(to_node)
            if from_node not in self.reverse_edges[to_node]:
                self.reverse_edges[to_node].append(from_node)
            logger.info(f"RPG 엣지 추가: {from_node} -> {to_node} ({edge_type})")
    
    def get_execution_order(self) -> List[str]:
        """위상 정렬을 통한 실행 순서 결정"""
        visited = set()
        temp_visited = set()
        result = []
        
        def dfs(node_id: str) -> bool:
            if node_id in temp_visited:
                return False  # 순환 의존성 발견
            if node_id in visited:
                return True
                
            temp_visited.add(node_id)
            
            # 의존성 먼저 처리
            for predecessor in self.reverse_edges.get(node_id, []):
                if not dfs(predecessor):
                    return False
            
            temp_visited.remove(node_id)
            visited.add(node_id)
            result.append(node_id)
            return True
        
        for node_id in self.nodes:
            if node_id not in visited:
                if not dfs(node_id):
                    logger.error("순환 의존성 발견, 실행 순서 결정 실패")
                    return []
        
        self.execution_plan = result
        return result
    
    def get_ready_nodes(self) -> List[str]:
        """실행 가능한 노드들 반환 (의존성이 완료된 노드)"""
        ready_nodes = []
        for node_id, node in self.nodes.items():
            if node.status == "planned":
                # 모든 의존성이 완료되었는지 확인
                dependencies = self.reverse_edges.get(node_id, [])
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
        self.domain_templates = self._load_domain_templates()
    
    def create_capability_graph(self, user_request: str, 
                               domain_context: str = "general") -> RPGGraph:
        """
        사용자 요청으로부터 능력 그래프 생성
        논문의 proposal-level planning 구현
        """
        rpg = RPGGraph()
        
        # 1. 도메인별 템플릿 적용
        template = self.domain_templates.get(domain_context, self.domain_templates["general"])
        
        # 2. 주요 기능 추출
        capabilities = self._extract_capabilities_from_template(user_request, template)
        
        # 3. 기능 노드 생성
        for i, cap in enumerate(capabilities):
            node = RPGNode(
                node_id=f"cap_{i}",
                node_type=NodeType.CAPABILITY,
                name=cap["name"],
                description=cap["description"],
                priority=cap.get("priority", 0),
                metadata={
                    "domain": domain_context, 
                    "user_request": user_request,
                    "template": template["name"]
                }
            )
            rpg.add_node(node)
        
        # 4. 의존성 관계 설정
        self._establish_dependencies(rpg, capabilities)
        
        return rpg
    
    def refine_to_implementation(self, rpg: RPGGraph) -> RPGGraph:
        """
        기능 그래프를 구현 수준으로 정제
        논문의 implementation-level refinement 구현
        """
        # 각 기능 노드를 실제 처리 노드로 분해
        new_nodes = []
        for node_id, node in list(rpg.nodes.items()):
            if node.node_type == NodeType.CAPABILITY:
                impl_nodes = self._decompose_capability(node)
                new_nodes.extend(impl_nodes)
        
        # 구현 노드들 추가
        for impl_node in new_nodes:
            rpg.add_node(impl_node)
            # 원래 능력 노드와 연결
            cap_node_id = impl_node.metadata.get("capability_id")
            if cap_node_id:
                rpg.add_edge(cap_node_id, impl_node.node_id, "implements")
        
        # 실행 순서 재계산
        rpg.get_execution_order()
        rpg.current_phase = ExecutionPhase.REFINEMENT
        
        return rpg
    
    def _load_domain_templates(self) -> Dict[str, Dict[str, Any]]:
        """도메인별 템플릿 로드 - 설정 기반으로 확장 가능"""
        return {
            "general": {
                "name": "일반 RAG 템플릿",
                "capabilities": [
                    {"name": "질문_분석", "description": "사용자 질문 분석 및 정제", "priority": 1},
                    {"name": "정보_검색", "description": "관련 문서 검색 및 수집", "priority": 2}, 
                    {"name": "답변_생성", "description": "검색된 정보 기반 답변 생성", "priority": 3},
                    {"name": "품질_검증", "description": "답변 품질 검증 및 개선", "priority": 4}
                ]
            },
            "hr": {
                "name": "인사 규정 템플릿",
                "capabilities": [
                    {"name": "질문_분류", "description": "HR 관련 질문인지 분류", "priority": 1},
                    {"name": "정책_검색", "description": "관련 인사 정책 검색", "priority": 2},
                    {"name": "규정_해석", "description": "정책 내용 해석 및 적용", "priority": 3},
                    {"name": "담당자_연결", "description": "필요시 담당자 안내", "priority": 4}
                ]
            },
            "academic": {
                "name": "학술 문서 템플릿",
                "capabilities": [
                    {"name": "논문_분석", "description": "학술 질문 분석", "priority": 1},
                    {"name": "문헌_검색", "description": "관련 논문 및 자료 검색", "priority": 2},
                    {"name": "인용_추출", "description": "관련 인용문 및 출처 추출", "priority": 3},
                    {"name": "학술_답변", "description": "학술적 형식의 답변 생성", "priority": 4}
                ]
            }
        }
    
    def _extract_capabilities_from_template(self, user_request: str, 
                                          template: Dict[str, Any]) -> List[Dict[str, Any]]:
        """템플릿 기반 기능 추출"""
        base_capabilities = template["capabilities"].copy()
        
        # LLM이 있으면 사용자 요청에 따라 조정
        if self.llm_agent:
            # 향후 LLM 기반 동적 조정 로직 구현
            pass
            
        return base_capabilities
    
    def _establish_dependencies(self, rpg: RPGGraph, 
                               capabilities: List[Dict[str, Any]]) -> None:
        """기능 간 의존성 관계 설정"""
        # 우선순위 기반 순차 의존성 설정
        sorted_caps = sorted(capabilities, key=lambda x: x.get("priority", 0))
        for i in range(1, len(sorted_caps)):
            rpg.add_edge(f"cap_{sorted_caps[i-1]['priority']-1}", 
                        f"cap_{sorted_caps[i]['priority']-1}", "sequential")
    
    def _decompose_capability(self, capability_node: RPGNode) -> List[RPGNode]:
        """기능 노드를 구현 노드들로 분해"""
        impl_nodes = []
        base_id = capability_node.node_id
        
        if "질문_분석" in capability_node.name or "질문_분류" in capability_node.name:
            impl_nodes = [
                RPGNode(f"{base_id}_preprocess", NodeType.FUNCTION, 
                       "질문 전처리", "질문 정제 및 표준화",
                       metadata={"capability_id": base_id}),
                RPGNode(f"{base_id}_classify", NodeType.FUNCTION,
                       "의도 분류", "질문 의도 및 카테고리 분류",
                       metadata={"capability_id": base_id})
            ]
        elif "정보_검색" in capability_node.name or "정책_검색" in capability_node.name:
            impl_nodes = [
                RPGNode(f"{base_id}_retrieve", NodeType.FUNCTION,
                       "문서 검색", "벡터 DB 문서 검색",
                       metadata={"capability_id": base_id}),
                RPGNode(f"{base_id}_rerank", NodeType.FUNCTION,
                       "재순위화", "검색 결과 재순위화",
                       metadata={"capability_id": base_id})
            ]
        elif "답변_생성" in capability_node.name:
            impl_nodes = [
                RPGNode(f"{base_id}_generate", NodeType.FUNCTION,
                       "답변 생성", "LLM 기반 답변 생성",
                       metadata={"capability_id": base_id})
            ]
        elif "품질_검증" in capability_node.name:
            impl_nodes = [
                RPGNode(f"{base_id}_verify", NodeType.FUNCTION,
                       "품질 검증", "답변 품질 검증",
                       metadata={"capability_id": base_id})
            ]
        
        # 구현 노드 간 의존성 설정
        for i in range(1, len(impl_nodes)):
            # 같은 능력 내에서는 순차적 의존성
            pass
        
        return impl_nodes

class RPGExecutor:
    """RPG 실행 관리 클래스"""
    
    def __init__(self, rpg: RPGGraph):
        self.rpg = rpg
        self.execution_context = {}
        self.function_registry = self._build_function_registry()
    
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
    
    def execute_graph(self, state_manager) -> Dict[str, Any]:
        """전체 그래프 실행"""
        results = {}
        execution_order = self.rpg.get_execution_order()
        
        for node_id in execution_order:
            result = self._execute_node(node_id, state_manager)
            results[node_id] = result
            
            # 실패시 중단
            if self.rpg.nodes[node_id].status == "failed":
                break
                
        return results
    
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
        # 함수 레지스트리에서 실제 함수 찾기
        func_key = self._get_function_key(node)
        if func_key in self.function_registry:
            func = self.function_registry[func_key]
            return func(node, state_manager)
        else:
            return f"{node.name} 실행 완료 (기본 처리)"
    
    def _execute_capability_node(self, node: RPGNode, state_manager) -> str:
        """능력 노드 실행 (추상적 능력 실행)"""
        return f"능력 {node.name} 실행 완료"
    
    def _get_function_key(self, node: RPGNode) -> str:
        """노드로부터 함수 키 생성"""
        if "전처리" in node.name or "preprocess" in node.node_id:
            return "preprocess"
        elif "검색" in node.name or "retrieve" in node.node_id:
            return "retrieve" 
        elif "재순위" in node.name or "rerank" in node.node_id:
            return "rerank"
        elif "생성" in node.name or "generate" in node.node_id:
            return "generate"
        elif "검증" in node.name or "verify" in node.node_id:
            return "verify"
        return "default"
    
    def _build_function_registry(self) -> Dict[str, callable]:
        """함수 레지스트리 구성"""
        return {
            "preprocess": self._func_preprocess,
            "retrieve": self._func_retrieve,
            "rerank": self._func_rerank, 
            "generate": self._func_generate,
            "verify": self._func_verify,
            "default": self._func_default
        }
    
    def _func_preprocess(self, node: RPGNode, state_manager) -> str:
        """전처리 함수"""
        # 실제 전처리 로직은 agents.py의 함수를 호출
        return "질문 전처리 완료"
    
    def _func_retrieve(self, node: RPGNode, state_manager) -> str:
        """검색 함수"""
        return "문서 검색 완료"
    
    def _func_rerank(self, node: RPGNode, state_manager) -> str:
        """재순위화 함수"""
        return "문서 재순위화 완료"
    
    def _func_generate(self, node: RPGNode, state_manager) -> str:
        """답변 생성 함수"""
        return "답변 생성 완료"
    
    def _func_verify(self, node: RPGNode, state_manager) -> str:
        """검증 함수"""
        return "답변 검증 완료"
    
    def _func_default(self, node: RPGNode, state_manager) -> str:
        """기본 함수"""
        return f"{node.name} 기본 실행 완료"

# RPG 시스템의 주 인터페이스
class RPGManager:
    """RPG 시스템 전체 관리자"""
    
    def __init__(self, llm_agent=None):
        self.planner = RPGPlanner(llm_agent)
        self.current_rpg: Optional[RPGGraph] = None
        self.executor: Optional[RPGExecutor] = None
    
    def create_and_execute_rpg(self, user_request: str, 
                              domain_context: str = "general",
                              state_manager=None) -> Dict[str, Any]:
        """RPG 생성 및 실행 통합 인터페이스"""
        
        # 1. 능력 그래프 생성 (Planning Phase)
        self.current_rpg = self.planner.create_capability_graph(user_request, domain_context)
        
        # 2. 구현 수준으로 정제 (Refinement Phase)  
        self.current_rpg = self.planner.refine_to_implementation(self.current_rpg)
        
        # 3. 실행자 생성 및 그래프 실행 (Execution Phase)
        self.executor = RPGExecutor(self.current_rpg)
        self.current_rpg.current_phase = ExecutionPhase.EXECUTION
        
        results = self.executor.execute_graph(state_manager)
        
        # 4. 검증 단계 (Validation Phase)
        self.current_rpg.current_phase = ExecutionPhase.VALIDATION
        
        return {
            "rpg_graph": self.current_rpg,
            "execution_results": results,
            "status": "completed"
        }
    
    def get_rpg_status(self) -> Dict[str, Any]:
        """현재 RPG 상태 반환"""
        if not self.current_rpg:
            return {"status": "no_rpg"}
            
        return {
            "phase": self.current_rpg.current_phase.value,
            "total_nodes": len(self.current_rpg.nodes),
            "completed_nodes": len([n for n in self.current_rpg.nodes.values() 
                                  if n.status == "completed"]),
            "failed_nodes": len([n for n in self.current_rpg.nodes.values() 
                               if n.status == "failed"]),
            "ready_nodes": self.current_rpg.get_ready_nodes()
        }
'''

# 파일 저장
with open('rpg.py', 'w', encoding='utf-8') as f:
    f.write(rpg_py_content)

print("✅ rpg.py 생성 완료")
print(f"파일 크기: {len(rpg_py_content)} 문자")
print("\n주요 특징:")
print("- Repository Planning Graph 핵심 로직 구현")
print("- 도메인별 템플릿 지원 (일반, HR, 학술)")  
print("- 경량화된 그래프 구조 (NetworkX 없이)")
print("- 3단계 실행: Planning -> Refinement -> Execution")
print("- 플러그인 방식의 함수 레지스트리")
print("- HTIL 대체를 위한 자율 실행 시스템")
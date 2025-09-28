# graph.py와 requirements.txt 생성
graph_py_content = '''# graph.py - 통합 그래프 오케스트레이션
# RPG와 LangGraph 통합, 동적 워크플로우 생성

from typing import Dict, Any, List, Optional, Callable, TypedDict
from langgraph.graph import StateGraph, END, START
from langgraph.graph.graph import CompiledGraph
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver
import asyncio
import logging
import json
import time

from state import ComposableState, create_initial_state
from rpg import RPGManager, RPGGraph, ExecutionPhase
from memory import MemoryManager
from tools import ToolRegistry, ToolExecutor
from agents import BaseAgent, LLMAgent, AutonomousAgent, CoordinatorAgent, AgentResult
from router import IntelligentRouter, RouteDecision, RouteType
from db import DatabaseManager
from utils import record_execution, profile, get_config

logger = logging.getLogger(__name__)

class GraphMode(Enum):
    """그래프 실행 모드"""
    STANDARD = "standard"       # 표준 RAG 모드
    RPG_ENHANCED = "rpg_enhanced"  # RPG 강화 모드
    AUTONOMOUS = "autonomous"   # 자율 모드
    COORDINATOR = "coordinator" # 조정 모드
    CUSTOM = "custom"          # 사용자 정의 모드

from enum import Enum

class DynamicGraphBuilder:
    """동적 그래프 빌더"""
    
    def __init__(self):
        self.nodes: Dict[str, Callable] = {}
        self.edges: List[Tuple[str, str]] = []
        self.conditional_edges: List[Dict[str, Any]] = []
        self.entry_point = START
        self.exit_points = [END]
        
    def add_node(self, name: str, func: Callable) -> 'DynamicGraphBuilder':
        """노드 추가"""
        self.nodes[name] = func
        return self
    
    def add_edge(self, from_node: str, to_node: str) -> 'DynamicGraphBuilder':
        """엣지 추가"""
        self.edges.append((from_node, to_node))
        return self
    
    def add_conditional_edge(self, from_node: str, condition_func: Callable, 
                           mapping: Dict[str, str]) -> 'DynamicGraphBuilder':
        """조건부 엣지 추가"""
        self.conditional_edges.append({
            "from_node": from_node,
            "condition_func": condition_func,
            "mapping": mapping
        })
        return self
    
    def build(self) -> StateGraph:
        """그래프 빌드"""
        graph = StateGraph(ComposableState)
        
        # 노드 추가
        for name, func in self.nodes.items():
            graph.add_node(name, func)
        
        # 일반 엣지 추가
        for from_node, to_node in self.edges:
            graph.add_edge(from_node, to_node)
        
        # 조건부 엣지 추가
        for edge_config in self.conditional_edges:
            graph.add_conditional_edges(
                edge_config["from_node"],
                edge_config["condition_func"],
                edge_config["mapping"]
            )
        
        # 시작점 설정
        if self.entry_point in self.nodes:
            graph.set_entry_point(self.entry_point)
        elif self.nodes:
            first_node = list(self.nodes.keys())[0]
            graph.add_edge(START, first_node)
        
        return graph

class GraphOrchestrator:
    """그래프 오케스트레이터 - 모든 구성요소 통합 관리"""
    
    def __init__(self):
        # 핵심 구성요소들
        self.memory_manager: Optional[MemoryManager] = None
        self.database_manager: Optional[DatabaseManager] = None
        self.tool_registry: Optional[ToolRegistry] = None
        self.tool_executor: Optional[ToolExecutor] = None
        self.rpg_manager: Optional[RPGManager] = None
        self.router: Optional[IntelligentRouter] = None
        
        # 에이전트들
        self.agents: Dict[str, BaseAgent] = {}
        
        # 그래프
        self.compiled_graph: Optional[CompiledGraph] = None
        self.graph_mode = GraphMode.STANDARD
        
        # 체크포인터
        self.checkpointer = MemorySaver()
        
    def initialize_components(self, config: Dict[str, Any] = None) -> bool:
        """모든 구성요소 초기화"""
        try:
            config = config or {}
            
            # 1. 메모리 매니저 초기화
            self.memory_manager = MemoryManager()
            
            # 2. 데이터베이스 매니저 초기화
            self.database_manager = DatabaseManager()
            
            # 3. 도구 시스템 초기화
            from tools import setup_default_tool_environment
            self.tool_registry, self.tool_executor = setup_default_tool_environment()
            
            # 4. RPG 매니저 초기화
            self.rpg_manager = RPGManager()
            
            # 5. 라우터 초기화
            self.router = IntelligentRouter(
                self.memory_manager, 
                self.tool_executor, 
                self.rpg_manager
            )
            
            # 6. 에이전트들 초기화
            self._initialize_agents()
            
            logger.info("모든 구성요소 초기화 완료")
            return True
            
        except Exception as e:
            logger.error(f"구성요소 초기화 실패: {str(e)}")
            return False
    
    def _initialize_agents(self) -> None:
        """에이전트들 초기화"""
        # LLM 에이전트들
        self.agents["llm_gen"] = LLMAgent("gen", "gen", self.memory_manager, self.tool_executor)
        self.agents["llm_router1"] = LLMAgent("router1", "router1", self.memory_manager, self.tool_executor)
        self.agents["llm_router2"] = LLMAgent("router2", "router2", self.memory_manager, self.tool_executor)
        
        # 자율 에이전트
        self.agents["autonomous"] = AutonomousAgent(
            "autonomous", self.memory_manager, self.tool_executor, self.rpg_manager
        )
        
        # 조정 에이전트
        coordinator = CoordinatorAgent("coordinator", self.memory_manager, self.tool_executor)
        for agent_name, agent in self.agents.items():
            if agent_name != "coordinator":
                coordinator.register_agent(agent)
        self.agents["coordinator"] = coordinator
    
    def build_graph(self, mode: GraphMode = GraphMode.STANDARD) -> bool:
        """그래프 빌드"""
        try:
            self.graph_mode = mode
            
            if mode == GraphMode.STANDARD:
                graph = self._build_standard_graph()
            elif mode == GraphMode.RPG_ENHANCED:
                graph = self._build_rpg_enhanced_graph()
            elif mode == GraphMode.AUTONOMOUS:
                graph = self._build_autonomous_graph()
            elif mode == GraphMode.COORDINATOR:
                graph = self._build_coordinator_graph()
            else:
                raise ValueError(f"지원하지 않는 그래프 모드: {mode}")
            
            # 그래프 컴파일
            self.compiled_graph = graph.compile(checkpointer=self.checkpointer)
            
            logger.info(f"그래프 빌드 완료: {mode.value}")
            return True
            
        except Exception as e:
            logger.error(f"그래프 빌드 실패: {str(e)}")
            return False
    
    def _build_standard_graph(self) -> StateGraph:
        """표준 RAG 그래프 빌드"""
        builder = DynamicGraphBuilder()
        
        return (builder
                .add_node("route_question", self._route_question_node)
                .add_node("process_hr_question", self._process_hr_question_node)
                .add_node("process_general_question", self._process_general_question_node)
                .add_node("retrieve_documents", self._retrieve_documents_node)
                .add_node("generate_answer", self._generate_answer_node)
                .add_node("general_chat", self._general_chat_node)
                .add_conditional_edge("route_question", self._routing_condition, {
                    "hr": "process_hr_question",
                    "general": "process_general_question", 
                    "chat": "general_chat"
                })
                .add_edge("process_hr_question", "retrieve_documents")
                .add_edge("process_general_question", "retrieve_documents")
                .add_edge("retrieve_documents", "generate_answer")
                .add_edge("generate_answer", END)
                .add_edge("general_chat", END)
                .build())
    
    def _build_rpg_enhanced_graph(self) -> StateGraph:
        """RPG 강화 그래프 빌드"""
        builder = DynamicGraphBuilder()
        
        return (builder
                .add_node("rpg_analysis", self._rpg_analysis_node)
                .add_node("route_with_rpg", self._route_with_rpg_node)
                .add_node("execute_rpg_plan", self._execute_rpg_plan_node)
                .add_node("retrieve_documents", self._retrieve_documents_node)
                .add_node("generate_answer", self._generate_answer_node)
                .add_node("validate_answer", self._validate_answer_node)
                .add_edge("rpg_analysis", "route_with_rpg")
                .add_conditional_edge("route_with_rpg", self._rpg_routing_condition, {
                    "execute_plan": "execute_rpg_plan",
                    "standard_rag": "retrieve_documents"
                })
                .add_edge("execute_rpg_plan", "validate_answer")
                .add_edge("retrieve_documents", "generate_answer")
                .add_edge("generate_answer", "validate_answer")
                .add_edge("validate_answer", END)
                .build())
    
    def _build_autonomous_graph(self) -> StateGraph:
        """자율 에이전트 그래프 빌드"""
        builder = DynamicGraphBuilder()
        
        return (builder
                .add_node("autonomous_planning", self._autonomous_planning_node)
                .add_node("autonomous_execution", self._autonomous_execution_node)
                .add_node("autonomous_evaluation", self._autonomous_evaluation_node)
                .add_node("autonomous_improvement", self._autonomous_improvement_node)
                .add_edge("autonomous_planning", "autonomous_execution")
                .add_edge("autonomous_execution", "autonomous_evaluation")
                .add_conditional_edge("autonomous_evaluation", self._autonomous_condition, {
                    "success": END,
                    "improve": "autonomous_improvement",
                    "retry": "autonomous_execution"
                })
                .add_edge("autonomous_improvement", "autonomous_execution")
                .build())
    
    def _build_coordinator_graph(self) -> StateGraph:
        """조정 에이전트 그래프 빌드"""
        builder = DynamicGraphBuilder()
        
        return (builder
                .add_node("coordinator_analysis", self._coordinator_analysis_node)
                .add_node("coordinator_delegation", self._coordinator_delegation_node)
                .add_node("coordinator_integration", self._coordinator_integration_node)
                .add_edge("coordinator_analysis", "coordinator_delegation")
                .add_edge("coordinator_delegation", "coordinator_integration")
                .add_edge("coordinator_integration", END)
                .build())
    
    # === 노드 구현 함수들 ===
    
    async def _route_question_node(self, state: ComposableState) -> ComposableState:
        """질문 라우팅 노드"""
        with profile("route_question"):
            try:
                if self.router:
                    decision = await self.router.route_request(state)
                    state.add_memory("routing_decision", decision.route_type.value)
                    
                    # 라우팅 결정을 상태에 저장
                    if hasattr(state, 'extensions'):
                        state.extensions["routing_decision"] = decision
                
                record_execution("graph", "route_question", 0.1, True)
                return state
                
            except Exception as e:
                logger.error(f"라우팅 노드 오류: {str(e)}")
                record_execution("graph", "route_question", 0.1, False, error=str(e))
                return state
    
    async def _process_hr_question_node(self, state: ComposableState) -> ComposableState:
        """HR 질문 처리 노드"""
        with profile("process_hr_question"):
            try:
                # HR 전용 처리 로직
                question = getattr(state, 'user_question', '')
                processed_question = f"[HR 질문] {question}"
                state.refined_question = processed_question
                state.is_hr_question = True
                
                # HR 도메인 컨텍스트 추가
                state.add_memory("domain_context", "hr")
                
                record_execution("graph", "process_hr_question", 0.1, True)
                return state
                
            except Exception as e:
                logger.error(f"HR 처리 노드 오류: {str(e)}")
                record_execution("graph", "process_hr_question", 0.1, False, error=str(e))
                return state
    
    async def _process_general_question_node(self, state: ComposableState) -> ComposableState:
        """일반 질문 처리 노드"""
        with profile("process_general_question"):
            try:
                question = getattr(state, 'user_question', '')
                state.refined_question = question
                state.is_hr_question = False
                
                state.add_memory("domain_context", "general")
                
                record_execution("graph", "process_general_question", 0.1, True)
                return state
                
            except Exception as e:
                logger.error(f"일반 처리 노드 오류: {str(e)}")
                record_execution("graph", "process_general_question", 0.1, False, error=str(e))
                return state
    
    async def _retrieve_documents_node(self, state: ComposableState) -> ComposableState:
        """문서 검색 노드"""
        with profile("retrieve_documents"):
            try:
                query = getattr(state, 'refined_question', '') or getattr(state, 'user_question', '')
                
                if self.database_manager:
                    # 활성 데이터베이스에서 검색
                    documents = await self.database_manager.search_in_active_db(query, top_k=5)
                    state.retrieved_docs = documents
                    
                    state.add_memory("retrieved_docs_count", len(documents))
                
                record_execution("graph", "retrieve_documents", 0.5, True, docs_found=len(documents) if documents else 0)
                return state
                
            except Exception as e:
                logger.error(f"문서 검색 노드 오류: {str(e)}")
                record_execution("graph", "retrieve_documents", 0.5, False, error=str(e))
                state.retrieved_docs = []
                return state
    
    async def _generate_answer_node(self, state: ComposableState) -> ComposableState:
        """답변 생성 노드"""
        with profile("generate_answer"):
            try:
                # LLM 에이전트를 통한 답변 생성
                llm_agent = self.agents.get("llm_gen")
                if llm_agent:
                    # 검색된 문서 컨텍스트 구성
                    docs_context = ""
                    if hasattr(state, 'retrieved_docs') and state.retrieved_docs:
                        docs_context = "\\n\\n".join([doc.page_content for doc in state.retrieved_docs[:3]])
                    
                    generation_task = f"""
                    다음 질문에 대해 제공된 문서들을 기반으로 정확하고 도움이 되는 답변을 생성해주세요.
                    
                    질문: {getattr(state, 'refined_question', '')}
                    
                    관련 문서:
                    {docs_context}
                    
                    정확하고 친절한 한국어로 답변해주세요.
                    """
                    
                    result = await llm_agent.execute(generation_task, {}, state)
                    
                    if result.success:
                        state.final_answer = result.data
                        state.answer_type = "generated"
                    else:
                        state.final_answer = "죄송합니다. 답변 생성 중 오류가 발생했습니다."
                        state.answer_type = "error"
                
                record_execution("graph", "generate_answer", 1.0, True)
                return state
                
            except Exception as e:
                logger.error(f"답변 생성 노드 오류: {str(e)}")
                record_execution("graph", "generate_answer", 1.0, False, error=str(e))
                state.final_answer = "답변 생성 중 오류가 발생했습니다."
                state.answer_type = "error"
                return state
    
    async def _general_chat_node(self, state: ComposableState) -> ComposableState:
        """일반 대화 노드"""
        with profile("general_chat"):
            try:
                question = getattr(state, 'user_question', '')
                
                # 간단한 대화 응답
                chat_responses = {
                    "안녕": "안녕하세요! 무엇을 도와드릴까요?",
                    "고마워": "천만에요! 언제든지 도움이 필요하시면 말씀해 주세요.",
                    "감사": "감사합니다! 더 궁금한 것이 있으시면 언제든 물어보세요."
                }
                
                response = "안녕하세요! 무엇을 도와드릴까요?"
                for keyword, resp in chat_responses.items():
                    if keyword in question:
                        response = resp
                        break
                
                state.final_answer = response
                state.answer_type = "chat"
                
                record_execution("graph", "general_chat", 0.1, True)
                return state
                
            except Exception as e:
                logger.error(f"일반 대화 노드 오류: {str(e)}")
                record_execution("graph", "general_chat", 0.1, False, error=str(e))
                state.final_answer = "안녕하세요!"
                state.answer_type = "chat"
                return state
    
    # RPG 강화 노드들
    async def _rpg_analysis_node(self, state: ComposableState) -> ComposableState:
        """RPG 분석 노드"""
        if self.rpg_manager:
            try:
                question = getattr(state, 'user_question', '')
                domain = state.memory_state.short_term.get("domain_context", "general") if hasattr(state, 'memory_state') else "general"
                
                rpg_result = self.rpg_manager.create_and_execute_rpg(question, domain, state)
                state.extensions["rpg_result"] = rpg_result
                
                return state
            except Exception as e:
                logger.error(f"RPG 분석 노드 오류: {str(e)}")
                return state
        return state
    
    async def _execute_rpg_plan_node(self, state: ComposableState) -> ComposableState:
        """RPG 계획 실행 노드"""
        # RPG 계획에 따른 실행 로직
        if "rpg_result" in getattr(state, 'extensions', {}):
            rpg_result = state.extensions["rpg_result"]
            # RPG 실행 결과를 최종 답변으로 설정
            if rpg_result.get("execution_results"):
                state.final_answer = "RPG 기반 처리가 완료되었습니다."
                state.answer_type = "rpg_generated"
        
        return state
    
    # 자율 에이전트 노드들
    async def _autonomous_planning_node(self, state: ComposableState) -> ComposableState:
        """자율 계획 노드"""
        autonomous_agent = self.agents.get("autonomous")
        if autonomous_agent:
            try:
                question = getattr(state, 'user_question', '')
                result = await autonomous_agent.execute(f"계획 수립: {question}", {}, state)
                state.extensions["autonomous_plan"] = result
            except Exception as e:
                logger.error(f"자율 계획 노드 오류: {str(e)}")
        return state
    
    async def _autonomous_execution_node(self, state: ComposableState) -> ComposableState:
        """자율 실행 노드"""
        autonomous_agent = self.agents.get("autonomous")
        if autonomous_agent:
            try:
                question = getattr(state, 'user_question', '')
                result = await autonomous_agent.execute(question, {}, state)
                
                if result.success:
                    state.final_answer = result.data or "자율 처리가 완료되었습니다."
                    state.answer_type = "autonomous_generated"
                    state.extensions["autonomous_result"] = result
                
            except Exception as e:
                logger.error(f"자율 실행 노드 오류: {str(e)}")
        return state
    
    # 조정 에이전트 노드들
    async def _coordinator_analysis_node(self, state: ComposableState) -> ComposableState:
        """조정 분석 노드"""
        coordinator = self.agents.get("coordinator")
        if coordinator:
            try:
                question = getattr(state, 'user_question', '')
                result = await coordinator.execute(f"분석: {question}", {}, state)
                state.extensions["coordinator_analysis"] = result
            except Exception as e:
                logger.error(f"조정 분석 노드 오류: {str(e)}")
        return state
    
    async def _coordinator_delegation_node(self, state: ComposableState) -> ComposableState:
        """조정 위임 노드"""
        coordinator = self.agents.get("coordinator")
        if coordinator:
            try:
                question = getattr(state, 'user_question', '')
                result = await coordinator.execute(question, {}, state)
                
                if result.success:
                    state.final_answer = result.data or "다중 에이전트 처리가 완료되었습니다."
                    state.answer_type = "coordinator_generated"
                    state.extensions["coordinator_result"] = result
                
            except Exception as e:
                logger.error(f"조정 위임 노드 오류: {str(e)}")
        return state
    
    # === 조건 함수들 ===
    
    def _routing_condition(self, state: ComposableState) -> str:
        """라우팅 조건 함수"""
        try:
            if hasattr(state, 'extensions') and "routing_decision" in state.extensions:
                decision = state.extensions["routing_decision"]
                
                if decision.route_type == RouteType.HR_SPECIFIC:
                    return "hr"
                elif decision.route_type == RouteType.GENERAL_CHAT:
                    return "chat"
                else:
                    return "general"
            
            # 기본값
            return "general"
            
        except Exception as e:
            logger.error(f"라우팅 조건 오류: {str(e)}")
            return "general"
    
    def _rpg_routing_condition(self, state: ComposableState) -> str:
        """RPG 라우팅 조건"""
        if "rpg_result" in getattr(state, 'extensions', {}):
            rpg_result = state.extensions["rpg_result"]
            if rpg_result.get("rpg_graph") and len(rpg_result["rpg_graph"].nodes) > 3:
                return "execute_plan"
        
        return "standard_rag"
    
    def _autonomous_condition(self, state: ComposableState) -> str:
        """자율 에이전트 조건"""
        if "autonomous_result" in getattr(state, 'extensions', {}):
            result = state.extensions["autonomous_result"]
            if isinstance(result, AgentResult) and result.success:
                return "success"
            else:
                return "improve"
        
        return "retry"
    
    # === 실행 인터페이스 ===
    
    async def run(self, user_question: str, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """그래프 실행"""
        try:
            # 초기 상태 생성
            initial_state = create_initial_state(user_question)
            
            # 그래프 실행
            if not self.compiled_graph:
                raise RuntimeError("그래프가 빌드되지 않았습니다")
            
            # 스레드 ID 생성 (세션 관리용)
            thread_id = f"session_{int(time.time())}"
            
            # 그래프 실행
            final_state = None
            async for event in self.compiled_graph.astream(
                initial_state, 
                config={"configurable": {"thread_id": thread_id}}
            ):
                if event and isinstance(event, dict):
                    # 마지막 상태 추출
                    for node_name, node_state in event.items():
                        if isinstance(node_state, ComposableState):
                            final_state = node_state
            
            # 결과 반환
            if final_state:
                return {
                    "success": True,
                    "answer": getattr(final_state, 'final_answer', ''),
                    "answer_type": getattr(final_state, 'answer_type', 'unknown'),
                    "retrieved_docs": len(getattr(final_state, 'retrieved_docs', [])),
                    "execution_path": getattr(final_state, 'execution_path', []),
                    "context": final_state.get_context_summary()
                }
            else:
                return {
                    "success": False,
                    "error": "그래프 실행 완료되지 않음"
                }
                
        except Exception as e:
            logger.error(f"그래프 실행 오류: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

# 팩토리 함수들
def create_graph_orchestrator(config: Dict[str, Any] = None) -> GraphOrchestrator:
    """그래프 오케스트레이터 생성"""
    orchestrator = GraphOrchestrator()
    
    if orchestrator.initialize_components(config):
        return orchestrator
    else:
        raise RuntimeError("그래프 오케스트레이터 초기화 실패")

def create_standard_rag_system() -> GraphOrchestrator:
    """표준 RAG 시스템 생성"""
    orchestrator = create_graph_orchestrator()
    orchestrator.build_graph(GraphMode.STANDARD)
    return orchestrator

def create_rpg_enhanced_system() -> GraphOrchestrator:
    """RPG 강화 시스템 생성"""
    orchestrator = create_graph_orchestrator()
    orchestrator.build_graph(GraphMode.RPG_ENHANCED)
    return orchestrator

def create_autonomous_system() -> GraphOrchestrator:
    """자율 시스템 생성"""
    orchestrator = create_graph_orchestrator()
    orchestrator.build_graph(GraphMode.AUTONOMOUS)
    return orchestrator

# 기존 인터페이스 호환 함수
async def get_compiled_graph(checkpointer=None):
    """기존 호환성을 위한 컴파일된 그래프 반환"""
    try:
        orchestrator = create_standard_rag_system()
        return orchestrator.compiled_graph
    except Exception as e:
        logger.error(f"컴파일된 그래프 생성 실패: {str(e)}")
        raise

# 메인 실행 함수
async def run_rag_system(user_question: str, mode: str = "standard") -> Dict[str, Any]:
    """RAG 시스템 실행 메인 인터페이스"""
    
    mode_mapping = {
        "standard": GraphMode.STANDARD,
        "rpg": GraphMode.RPG_ENHANCED,
        "autonomous": GraphMode.AUTONOMOUS,
        "coordinator": GraphMode.COORDINATOR
    }
    
    graph_mode = mode_mapping.get(mode, GraphMode.STANDARD)
    
    orchestrator = create_graph_orchestrator()
    orchestrator.build_graph(graph_mode)
    
    return await orchestrator.run(user_question)
'''

# requirements.txt 업데이트
requirements_content = '''# LangGraph RAG 시스템 의존성
# 기존 라이브러리 + 새로운 추가

# LangChain 생태계
langchain>=0.3.0
langchain-community>=0.3.0
langchain-core>=0.3.0
langchain-openai>=0.2.0
langchain-pinecone>=0.2.0
langgraph>=0.2.0

# 벡터 데이터베이스
pinecone-client>=5.0.0
faiss-cpu>=1.8.0

# AI/ML 라이브러리  
openai>=1.0.0
numpy>=1.24.0

# 문서 처리
PyPDF2>=3.0.0
python-docx>=1.1.0

# 웹 및 API
requests>=2.31.0
aiohttp>=3.9.0
httpx>=0.27.0

# 데이터 처리
pandas>=2.0.0
pyyaml>=6.0.0

# 비동기 처리
asyncio-throttle>=1.0.2

# 유틸리티
python-dotenv>=1.0.0
pydantic>=2.0.0
typing-extensions>=4.8.0

# 네트워크 그래프 (RPG용)
# networkx>=3.0  # 경량화를 위해 제거, 자체 구현 사용

# 개발 도구 (선택사항)
pytest>=7.4.0
pytest-asyncio>=0.23.0
black>=23.0.0
'''

# 파일들 저장
with open('graph.py', 'w', encoding='utf-8') as f:
    f.write(graph_py_content)

with open('requirements.txt', 'w', encoding='utf-8') as f:
    f.write(requirements_content)

print("✅ graph.py 및 requirements.txt 생성 완료")
print(f"graph.py 크기: {len(graph_py_content)} 문자")
print(f"requirements.txt 항목: {len(requirements_content.split('\\n'))} 줄")
print("\n전체 리팩터링 완료!")
print("생성된 파일들:")
print("1. state.py - 통합 상태 관리")  
print("2. rpg.py - Repository Planning Graph")
print("3. memory.py - Agentic AI Memory 시스템")
print("4. tools.py - Tool 인터페이스 관리") 
print("5. agents.py - Agentic 구성 요소")
print("6. db.py - 벤더 독립적 데이터베이스")
print("7. router.py - 지능형 라우팅")
print("8. utils.py - 공통 유틸리티")
print("9. graph.py - 통합 그래프 오케스트레이션")
print("10. requirements.txt - 의존성 관리")
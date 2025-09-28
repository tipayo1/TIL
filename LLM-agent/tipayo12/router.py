# router.py - 지능형 라우팅 시스템
# 기존 router.py 확장 - RPG 기반 동적 라우팅

from typing import Dict, Any, Optional, List, Callable, Tuple
import logging
import asyncio
from enum import Enum

from state import ComposableState
from rpg import RPGManager, RPGGraph
from agents import BaseAgent, LLMAgent, AutonomousAgent, CoordinatorAgent
from memory import MemoryManager
from tools import ToolExecutor
from utils import get_llm, record_execution, profile

logger = logging.getLogger(__name__)

class RouteType(Enum):
    """라우팅 타입"""
    RAG_ANSWER = "rag_answer"
    GENERAL_CHAT = "general_chat"
    HR_SPECIFIC = "hr_specific"
    COMPLEX_TASK = "complex_task"
    AUTONOMOUS_MODE = "autonomous_mode"
    COORDINATOR_MODE = "coordinator_mode"
    ERROR_FALLBACK = "error_fallback"

class RouteDecision:
    """라우팅 결정"""

    def __init__(self, route_type: RouteType, confidence: float, 
                 reasoning: str = "", metadata: Dict[str, Any] = None):
        self.route_type = route_type
        self.confidence = confidence
        self.reasoning = reasoning
        self.metadata = metadata or {}
        self.timestamp = asyncio.get_event_loop().time()

class IntelligentRouter:
    """지능형 라우터"""

    def __init__(self, memory_manager: Optional[MemoryManager] = None,
                 tool_executor: Optional[ToolExecutor] = None,
                 rpg_manager: Optional[RPGManager] = None):

        self.memory_manager = memory_manager
        self.tool_executor = tool_executor
        self.rpg_manager = rpg_manager

        # 라우팅 에이전트들
        self.llm_router1 = LLMAgent("router1", "router1", memory_manager, tool_executor)
        self.llm_router2 = LLMAgent("router2", "router2", memory_manager, tool_executor)

        # 라우팅 규칙
        self.routing_rules = self._build_routing_rules()

        # 라우팅 히스토리
        self.routing_history: List[RouteDecision] = []

    def _build_routing_rules(self) -> Dict[str, Dict[str, Any]]:
        """라우팅 규칙 구성"""
        return {
            "simple_qa": {
                "patterns": ["뭐야", "뭔가요", "알려줘", "설명해"],
                "route": RouteType.RAG_ANSWER,
                "confidence_threshold": 0.8
            },
            "hr_keywords": {
                "patterns": ["휴가", "연차", "급여", "복지", "인사", "규정"],
                "route": RouteType.HR_SPECIFIC,
                "confidence_threshold": 0.9
            },
            "complex_tasks": {
                "patterns": ["분석해", "계획", "전략", "종합", "단계별"],
                "route": RouteType.COMPLEX_TASK,
                "confidence_threshold": 0.7
            },
            "autonomous_indicators": {
                "patterns": ["자동으로", "알아서", "최적화", "개선"],
                "route": RouteType.AUTONOMOUS_MODE,
                "confidence_threshold": 0.8
            },
            "general_chat": {
                "patterns": ["안녕", "고마워", "감사", "반가워"],
                "route": RouteType.GENERAL_CHAT,
                "confidence_threshold": 0.6
            }
        }

    async def route_request(self, state: ComposableState) -> RouteDecision:
        """요청 라우팅"""

        with profile("intelligent_routing"):
            try:
                # 1. 빠른 규칙 기반 라우팅 시도
                rule_decision = await self._rule_based_routing(state)

                if rule_decision.confidence >= 0.9:
                    self._record_routing_decision(rule_decision)
                    return rule_decision

                # 2. LLM 기반 지능형 라우팅
                llm_decision = await self._llm_based_routing(state)

                # 3. RPG 기반 동적 라우팅 (복잡한 작업의 경우)
                if llm_decision.route_type in [RouteType.COMPLEX_TASK, RouteType.AUTONOMOUS_MODE]:
                    rpg_decision = await self._rpg_based_routing(state, llm_decision)
                    if rpg_decision:
                        self._record_routing_decision(rpg_decision)
                        return rpg_decision

                # 4. 최종 결정 (규칙 기반 + LLM 기반 결합)
                final_decision = self._combine_routing_decisions(rule_decision, llm_decision)
                self._record_routing_decision(final_decision)

                return final_decision

            except Exception as e:
                logger.error(f"라우팅 오류: {str(e)}")
                error_decision = RouteDecision(
                    route_type=RouteType.ERROR_FALLBACK,
                    confidence=1.0,
                    reasoning=f"라우팅 오류로 인한 폴백: {str(e)}"
                )
                self._record_routing_decision(error_decision)
                return error_decision

    async def _rule_based_routing(self, state: ComposableState) -> RouteDecision:
        """규칙 기반 라우팅"""

        question = getattr(state, 'user_question', '') or getattr(state, 'refined_question', '')
        if not question:
            return RouteDecision(RouteType.ERROR_FALLBACK, 0.5, "질문이 없음")

        question_lower = question.lower()
        best_match = None
        best_score = 0.0

        for rule_name, rule_config in self.routing_rules.items():
            score = 0.0
            matched_patterns = []

            for pattern in rule_config["patterns"]:
                if pattern in question_lower:
                    score += 1.0
                    matched_patterns.append(pattern)

            # 패턴 매칭 점수 정규화
            if rule_config["patterns"]:
                score = score / len(rule_config["patterns"])

                if score > best_score:
                    best_score = score
                    best_match = rule_config
                    best_match["matched_patterns"] = matched_patterns

        if best_match and best_score >= best_match["confidence_threshold"]:
            return RouteDecision(
                route_type=best_match["route"],
                confidence=best_score,
                reasoning=f"규칙 기반 매칭: {best_match['matched_patterns']}",
                metadata={"rule_based": True, "matched_patterns": best_match["matched_patterns"]}
            )

        return RouteDecision(RouteType.RAG_ANSWER, 0.5, "기본 RAG 라우팅")

    async def _llm_based_routing(self, state: ComposableState) -> RouteDecision:
        """LLM 기반 지능형 라우팅"""

        question = getattr(state, 'user_question', '') or getattr(state, 'refined_question', '')

        # 라우팅 전용 프롬프트
        routing_prompt = f"""
        다음 사용자 질문을 분석하여 적절한 처리 방식을 결정해주세요.

        질문: "{question}"

        가능한 라우팅 옵션:
        1. rag_answer: 일반적인 RAG 기반 질답
        2. hr_specific: HR/인사 관련 전문 처리
        3. complex_task: 복잡한 다단계 작업
        4. autonomous_mode: 자율 에이전트 처리 필요
        5. coordinator_mode: 다중 에이전트 조정 필요
        6. general_chat: 일반 대화

        다음 JSON 형식으로 답변해주세요:
        {{
            "route_type": "선택된_라우팅_타입",
            "confidence": 0.0-1.0,
            "reasoning": "라우팅 결정 이유"
        }}
        """

        try:
            llm_result = await self.llm_router1.execute(routing_prompt, {}, state)

            if llm_result.success and isinstance(llm_result.data, dict):
                route_data = llm_result.data
            else:
                # JSON 파싱 시도
                import json
                route_data = json.loads(llm_result.data)

            route_type_str = route_data.get("route_type", "rag_answer")

            # 문자열을 RouteType enum으로 변환
            try:
                route_type = RouteType(route_type_str.upper())
            except ValueError:
                route_type = RouteType.RAG_ANSWER

            return RouteDecision(
                route_type=route_type,
                confidence=route_data.get("confidence", 0.7),
                reasoning=route_data.get("reasoning", "LLM 기반 라우팅"),
                metadata={"llm_based": True}
            )

        except Exception as e:
            logger.error(f"LLM 라우팅 오류: {str(e)}")
            return RouteDecision(RouteType.RAG_ANSWER, 0.5, f"LLM 라우팅 오류: {str(e)}")

    async def _rpg_based_routing(self, state: ComposableState, 
                                base_decision: RouteDecision) -> Optional[RouteDecision]:
        """RPG 기반 동적 라우팅"""

        if not self.rpg_manager:
            return None

        question = getattr(state, 'user_question', '') or getattr(state, 'refined_question', '')

        try:
            # RPG 그래프 생성 및 분석
            rpg_result = self.rpg_manager.create_and_execute_rpg(
                question, 
                "general", 
                state
            )

            rpg_graph = rpg_result.get("rpg_graph")
            if not rpg_graph:
                return None

            # RPG 분석 결과에 따른 라우팅 조정
            node_count = len(rpg_graph.nodes)
            complexity_score = min(1.0, node_count / 10.0)  # 노드 수 기반 복잡도

            # 복잡도에 따른 라우팅 타입 조정
            if complexity_score >= 0.8:
                adjusted_route = RouteType.COORDINATOR_MODE
            elif complexity_score >= 0.5:
                adjusted_route = RouteType.AUTONOMOUS_MODE
            else:
                adjusted_route = base_decision.route_type

            return RouteDecision(
                route_type=adjusted_route,
                confidence=min(1.0, base_decision.confidence + complexity_score * 0.2),
                reasoning=f"RPG 기반 조정: 복잡도 {complexity_score:.2f}, 노드 {node_count}개",
                metadata={
                    "rpg_based": True,
                    "node_count": node_count,
                    "complexity_score": complexity_score,
                    "original_route": base_decision.route_type.value
                }
            )

        except Exception as e:
            logger.error(f"RPG 라우팅 오류: {str(e)}")
            return None

    def _combine_routing_decisions(self, rule_decision: RouteDecision, 
                                  llm_decision: RouteDecision) -> RouteDecision:
        """라우팅 결정 결합"""

        # 신뢰도가 높은 결정 선택
        if rule_decision.confidence >= llm_decision.confidence:
            primary = rule_decision
            secondary = llm_decision
        else:
            primary = llm_decision
            secondary = rule_decision

        # 결합된 메타데이터
        combined_metadata = {
            **primary.metadata,
            "secondary_route": secondary.route_type.value,
            "secondary_confidence": secondary.confidence,
            "combined": True
        }

        return RouteDecision(
            route_type=primary.route_type,
            confidence=primary.confidence,
            reasoning=f"주결정: {primary.reasoning} | 부결정: {secondary.reasoning}",
            metadata=combined_metadata
        )

    def _record_routing_decision(self, decision: RouteDecision) -> None:
        """라우팅 결정 기록"""
        self.routing_history.append(decision)

        # 메모리에 라우팅 패턴 저장
        if self.memory_manager:
            self.memory_manager.store(
                f"routing_decision_{int(decision.timestamp)}",
                {
                    "route_type": decision.route_type.value,
                    "confidence": decision.confidence,
                    "reasoning": decision.reasoning
                },
                memory_type="short_term"
            )

        # 실행 기록
        record_execution(
            "router", 
            decision.route_type.value, 
            0.1,  # 라우팅 시간
            True
        )

        logger.info(f"라우팅 결정: {decision.route_type.value} (신뢰도: {decision.confidence:.3f})")

    def get_routing_stats(self) -> Dict[str, Any]:
        """라우팅 통계"""
        if not self.routing_history:
            return {"total_routes": 0}

        route_counts = {}
        confidence_sum = 0.0

        for decision in self.routing_history:
            route_type = decision.route_type.value
            route_counts[route_type] = route_counts.get(route_type, 0) + 1
            confidence_sum += decision.confidence

        return {
            "total_routes": len(self.routing_history),
            "route_distribution": route_counts,
            "avg_confidence": confidence_sum / len(self.routing_history),
            "recent_routes": [d.route_type.value for d in self.routing_history[-10:]]
        }

# 라우팅 함수들 (기존 인터페이스 호환)
def determine_hr_question(state: ComposableState) -> str:
    """HR 질문 여부 판별 (기존 호환)"""
    try:
        # 간단한 키워드 기반 판별
        question = getattr(state, 'user_question', '') or getattr(state, 'refined_question', '')
        hr_keywords = ["휴가", "연차", "급여", "복지", "인사", "규정", "정책"]

        if any(keyword in question for keyword in hr_keywords):
            return "hr"
        else:
            return "non_hr"

    except Exception as e:
        logger.error(f"HR 판별 오류: {str(e)}")
        return "non_hr"

def route_to_rag_or_general(state: ComposableState) -> str:
    """RAG 또는 일반 채팅 라우팅 (기존 호환)"""
    try:
        question = getattr(state, 'user_question', '') or getattr(state, 'refined_question', '')

        # 일반 대화 키워드
        general_keywords = ["안녕", "고마워", "감사", "반가워", "잘 지내", "어때"]

        if any(keyword in question for keyword in general_keywords):
            return "general_chat"
        else:
            return "rag_answer"

    except Exception as e:
        logger.error(f"RAG/일반 라우팅 오류: {str(e)}")
        return "rag_answer"

# 고급 라우팅 팩토리
def create_intelligent_router(memory_manager: MemoryManager = None,
                             tool_executor: ToolExecutor = None, 
                             rpg_manager: RPGManager = None) -> IntelligentRouter:
    """지능형 라우터 생성"""
    return IntelligentRouter(memory_manager, tool_executor, rpg_manager)

# 라우팅 미들웨어
class RoutingMiddleware:
    """라우팅 미들웨어"""

    def __init__(self, router: IntelligentRouter):
        self.router = router
        self.pre_hooks: List[Callable] = []
        self.post_hooks: List[Callable] = []

    def add_pre_hook(self, hook: Callable) -> None:
        """전처리 훅 추가"""
        self.pre_hooks.append(hook)

    def add_post_hook(self, hook: Callable) -> None:
        """후처리 훅 추가"""
        self.post_hooks.append(hook)

    async def process_request(self, state: ComposableState) -> RouteDecision:
        """요청 처리 (훅 포함)"""

        # 전처리 훅 실행
        for hook in self.pre_hooks:
            try:
                await hook(state)
            except Exception as e:
                logger.error(f"전처리 훅 오류: {str(e)}")

        # 라우팅 실행
        decision = await self.router.route_request(state)

        # 후처리 훅 실행
        for hook in self.post_hooks:
            try:
                await hook(state, decision)
            except Exception as e:
                logger.error(f"후처리 훅 오류: {str(e)}")

        return decision

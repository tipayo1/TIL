# agents.py - Agentic AI 구성 요소
# LLM, Autonomy 요소를 포함한 지능형 에이전트 시스템

from typing import Dict, List, Any, Optional, Union, Callable, Tuple
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import asyncio
import json
import logging
import time
from enum import Enum

from state import ComposableState
from memory import MemoryManager
from tools import ToolRegistry, ToolExecutor, ToolResult
from rpg import RPGManager, RPGGraph
from utils import get_llm, PromptTemplate

logger = logging.getLogger(__name__)

class AgentType(Enum):
    """에이전트 타입"""
    LLM_AGENT = "llm_agent"              # LLM 기반 에이전트
    AUTONOMOUS_AGENT = "autonomous_agent" # 자율 에이전트
    COORDINATOR_AGENT = "coordinator_agent" # 조정 에이전트
    SPECIALIST_AGENT = "specialist_agent" # 전문 에이전트

class AgentStatus(Enum):
    """에이전트 상태"""
    IDLE = "idle"
    THINKING = "thinking"
    ACTING = "acting"
    WAITING = "waiting"
    ERROR = "error"

@dataclass
class AgentResult:
    """에이전트 실행 결과"""
    success: bool
    data: Any = None
    reasoning: str = ""
    actions_taken: List[str] = field(default_factory=list)
    error: Optional[str] = None
    execution_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

class BaseAgent(ABC):
    """기본 에이전트 추상 클래스"""

    def __init__(self, name: str, agent_type: AgentType, 
                 memory_manager: Optional[MemoryManager] = None,
                 tool_executor: Optional[ToolExecutor] = None):
        self.name = name
        self.agent_type = agent_type
        self.status = AgentStatus.IDLE
        self.memory_manager = memory_manager
        self.tool_executor = tool_executor
        self.execution_count = 0
        self.last_execution = None
        self.config = {}

    @abstractmethod
    async def execute(self, task: str, context: Dict[str, Any], 
                     state: ComposableState) -> AgentResult:
        """에이전트 실행"""
        pass

    @abstractmethod
    def can_handle_task(self, task: str, context: Dict[str, Any]) -> bool:
        """작업 처리 가능 여부 판단"""
        pass

    def update_status(self, status: AgentStatus) -> None:
        """상태 업데이트"""
        self.status = status
        logger.debug(f"에이전트 {self.name} 상태 변경: {status.value}")

    def update_execution_stats(self) -> None:
        """실행 통계 업데이트"""
        self.execution_count += 1
        self.last_execution = time.time()

    def get_agent_info(self) -> Dict[str, Any]:
        """에이전트 정보 반환"""
        return {
            "name": self.name,
            "type": self.agent_type.value,
            "status": self.status.value,
            "execution_count": self.execution_count,
            "last_execution": self.last_execution,
            "has_memory": self.memory_manager is not None,
            "has_tools": self.tool_executor is not None
        }

class LLMAgent(BaseAgent):
    """LLM 기반 에이전트 - Agentic AI의 LLM 구성요소"""

    def __init__(self, name: str = "llm_agent", model_role: str = "gen",
                 memory_manager: Optional[MemoryManager] = None,
                 tool_executor: Optional[ToolExecutor] = None):
        super().__init__(name, AgentType.LLM_AGENT, memory_manager, tool_executor)
        self.llm = get_llm(model_role)
        self.model_role = model_role
        self.prompt_templates = self._load_prompt_templates()
        self.reasoning_history = []

    async def execute(self, task: str, context: Dict[str, Any], 
                     state: ComposableState) -> AgentResult:
        """LLM 에이전트 실행"""
        start_time = time.time()
        self.update_status(AgentStatus.THINKING)

        try:
            # 1. 메모리에서 관련 컨텍스트 조회
            memory_context = self._get_memory_context(task)

            # 2. 프롬프트 구성
            prompt = self._build_prompt(task, context, memory_context, state)

            # 3. LLM 호출
            response = await self._invoke_llm(prompt)

            # 4. 응답 파싱
            parsed_result = self._parse_llm_response(response)

            # 5. 메모리에 저장
            if self.memory_manager:
                self._store_to_memory(task, parsed_result)

            # 6. 추론 기록 저장
            reasoning_record = {
                "task": task,
                "prompt": prompt[:500],  # 일부만 저장
                "response": response[:500],
                "timestamp": time.time()
            }
            self.reasoning_history.append(reasoning_record)

            self.update_status(AgentStatus.IDLE)
            self.update_execution_stats()

            return AgentResult(
                success=True,
                data=parsed_result,
                reasoning=self._extract_reasoning(response),
                actions_taken=["llm_inference"],
                execution_time=time.time() - start_time,
                metadata={"model_role": self.model_role}
            )

        except Exception as e:
            self.update_status(AgentStatus.ERROR)
            logger.error(f"LLM 에이전트 실행 오류: {str(e)}")

            return AgentResult(
                success=False,
                error=str(e),
                execution_time=time.time() - start_time
            )

    def can_handle_task(self, task: str, context: Dict[str, Any]) -> bool:
        """LLM 처리 가능 여부 판단"""
        # LLM은 대부분의 텍스트 기반 작업 처리 가능
        if not isinstance(task, str) or not task.strip():
            return False

        # 특정 도메인 검증 (필요시)
        if self.model_role == "router1" and "분류" not in task.lower():
            return False
        if self.model_role == "router2" and "라우팅" not in task.lower():
            return False

        return True

    def _get_memory_context(self, task: str) -> Dict[str, Any]:
        """메모리에서 관련 컨텍스트 조회"""
        if not self.memory_manager:
            return {}

        return self.memory_manager.get_context(task, context_size=3)

    def _build_prompt(self, task: str, context: Dict[str, Any], 
                     memory_context: Dict[str, Any], state: ComposableState) -> str:
        """프롬프트 구성"""
        # 작업 타입 추론
        task_type = self._infer_task_type(task)
        template = self.prompt_templates.get(task_type, self.prompt_templates["default"])

        # 템플릿에 컨텍스트 주입
        prompt = template.format(
            task=task,
            context=json.dumps(context, ensure_ascii=False, indent=2),
            memory_context=json.dumps(memory_context, ensure_ascii=False, indent=2),
            current_time=time.strftime("%Y-%m-%d %H:%M:%S"),
            agent_name=self.name
        )

        return prompt

    async def _invoke_llm(self, prompt: str) -> str:
        """LLM 호출"""
        try:
            response = await asyncio.to_thread(self.llm.invoke, prompt)
            return response.content if hasattr(response, 'content') else str(response)
        except Exception as e:
            logger.error(f"LLM 호출 실패: {str(e)}")
            raise

    def _parse_llm_response(self, response: str) -> Any:
        """LLM 응답 파싱"""
        try:
            # JSON 형태 응답 시도
            if response.strip().startswith('{') and response.strip().endswith('}'):
                return json.loads(response)

            # 일반 텍스트 응답
            return response.strip()

        except json.JSONDecodeError:
            return response.strip()

    def _store_to_memory(self, task: str, result: Any) -> None:
        """메모리에 저장"""
        if self.memory_manager:
            memory_key = f"llm_result_{int(time.time())}"
            self.memory_manager.store(
                memory_key, 
                {"task": task, "result": result},
                memory_type="short_term"
            )

    def _extract_reasoning(self, response: str) -> str:
        """추론 과정 추출"""
        # 응답에서 추론 과정을 추출하는 로직
        if "이유:" in response:
            return response.split("이유:")[1].split("\n")[0].strip()
        elif "추론:" in response:
            return response.split("추론:")[1].split("\n")[0].strip()
        return ""

    def _infer_task_type(self, task: str) -> str:
        """작업 타입 추론"""
        task_lower = task.lower()

        if any(word in task_lower for word in ["분류", "판별", "구분"]):
            return "classification"
        elif any(word in task_lower for word in ["검색", "조회", "찾기"]):
            return "search"
        elif any(word in task_lower for word in ["생성", "작성", "만들기"]):
            return "generation"
        elif any(word in task_lower for word in ["분석", "해석", "검토"]):
            return "analysis"
        else:
            return "default"

    def _load_prompt_templates(self) -> Dict[str, str]:
        """프롬프트 템플릿 로드"""
        return {
            "classification": """
당신은 전문 분류 AI입니다.

작업: {task}
컨텍스트: {context}
메모리 컨텍스트: {memory_context}

위 정보를 바탕으로 정확하게 분류해주세요.
분류 결과와 함께 이유도 함께 제공해주세요.

응답 형식:
분류: [결과]
이유: [분류 근거]
            """.strip(),

            "search": """
당신은 정보 검색 전문 AI입니다.

작업: {task}
컨텍스트: {context}
메모리 컨텍스트: {memory_context}

관련 정보를 찾아서 정확하고 유용한 답변을 제공해주세요.
            """.strip(),

            "generation": """
당신은 콘텐츠 생성 전문 AI입니다.

작업: {task}
컨텍스트: {context}
메모리 컨텍스트: {memory_context}

요구사항에 맞는 고품질 콘텐츠를 생성해주세요.
            """.strip(),

            "analysis": """
당신은 분석 전문 AI입니다.

작업: {task}
컨텍스트: {context}
메모리 컨텍스트: {memory_context}

주어진 정보를 체계적으로 분석하고 인사이트를 제공해주세요.
            """.strip(),

            "default": """
당신은 도움이 되는 AI 어시스턴트입니다.

작업: {task}
컨텍스트: {context}
메모리 컨텍스트: {memory_context}
현재 시간: {current_time}
에이전트: {agent_name}

주어진 작업을 정확하고 친절하게 수행해주세요.
            """.strip()
        }

class AutonomousAgent(BaseAgent):
    """자율 에이전트 - Agentic AI의 Autonomy 구성요소"""

    def __init__(self, name: str = "autonomous_agent",
                 memory_manager: Optional[MemoryManager] = None,
                 tool_executor: Optional[ToolExecutor] = None,
                 rpg_manager: Optional[RPGManager] = None):
        super().__init__(name, AgentType.AUTONOMOUS_AGENT, memory_manager, tool_executor)
        self.rpg_manager = rpg_manager
        self.llm_agent = LLMAgent("autonomous_llm", "gen", memory_manager, tool_executor)
        self.goal_stack = []  # 목표 스택
        self.action_history = []
        self.max_iterations = 10  # 무한루프 방지

    async def execute(self, task: str, context: Dict[str, Any], 
                     state: ComposableState) -> AgentResult:
        """자율 에이전트 실행 - 목표 지향적 자율 행동"""
        start_time = time.time()
        self.update_status(AgentStatus.THINKING)

        try:
            # 1. 목표 설정 및 계획 수립
            goal = await self._set_goal(task, context, state)
            plan = await self._create_plan(goal, context, state)

            # 2. RPG 활용 계획 정제
            if self.rpg_manager:
                rpg_result = self.rpg_manager.create_and_execute_rpg(
                    task, context.get("domain", "general"), state
                )
                plan = self._integrate_rpg_plan(plan, rpg_result)

            self.update_status(AgentStatus.ACTING)

            # 3. 계획 실행
            execution_results = await self._execute_plan(plan, context, state)

            # 4. 결과 평가 및 개선
            evaluation = await self._evaluate_results(goal, execution_results, state)

            # 5. 필요시 재시도 또는 개선
            if not evaluation["success"] and evaluation.get("retry_recommended"):
                improved_plan = await self._improve_plan(plan, execution_results, evaluation)
                execution_results = await self._execute_plan(improved_plan, context, state)

            self.update_status(AgentStatus.IDLE)
            self.update_execution_stats()

            return AgentResult(
                success=evaluation["success"],
                data=execution_results,
                reasoning=evaluation.get("reasoning", ""),
                actions_taken=self.action_history.copy(),
                execution_time=time.time() - start_time,
                metadata={
                    "goal": goal,
                    "plan_steps": len(plan),
                    "used_rpg": self.rpg_manager is not None
                }
            )

        except Exception as e:
            self.update_status(AgentStatus.ERROR)
            logger.error(f"자율 에이전트 실행 오류: {str(e)}")

            return AgentResult(
                success=False,
                error=str(e),
                execution_time=time.time() - start_time
            )

    def can_handle_task(self, task: str, context: Dict[str, Any]) -> bool:
        """자율 처리 가능 여부 판단"""
        # 복잡한 다단계 작업에 적합
        complexity_indicators = [
            "여러", "단계", "계획", "자동", "지능적", 
            "최적화", "개선", "분석 후", "종합적"
        ]

        return any(indicator in task for indicator in complexity_indicators)

    async def _set_goal(self, task: str, context: Dict[str, Any], 
                       state: ComposableState) -> Dict[str, Any]:
        """목표 설정"""
        goal_prompt = f"""
        다음 작업에 대한 명확한 목표를 설정해주세요:

        작업: {task}
        컨텍스트: {json.dumps(context, ensure_ascii=False, indent=2)}

        목표는 다음 형식으로 JSON으로 답변해주세요:
        {{
            "primary_goal": "주요 목표",
            "sub_goals": ["하위 목표1", "하위 목표2"],
            "success_criteria": ["성공 기준1", "성공 기준2"],
            "constraints": ["제약 조건1", "제약 조건2"]
        }}
        """

        llm_result = await self.llm_agent.execute(goal_prompt, context, state)

        try:
            if isinstance(llm_result.data, dict):
                return llm_result.data
            else:
                return json.loads(llm_result.data)
        except:
            # 기본 목표 구조
            return {
                "primary_goal": task,
                "sub_goals": [task],
                "success_criteria": ["작업 완료"],
                "constraints": []
            }

    async def _create_plan(self, goal: Dict[str, Any], context: Dict[str, Any], 
                          state: ComposableState) -> List[Dict[str, Any]]:
        """실행 계획 수립"""
        plan_prompt = f"""
        다음 목표를 달성하기 위한 단계별 실행 계획을 수립해주세요:

        목표: {json.dumps(goal, ensure_ascii=False, indent=2)}

        계획은 다음 형식으로 JSON 배열로 답변해주세요:
        [
            {{
                "step": 1,
                "action": "수행할 행동",
                "method": "실행 방법",
                "expected_output": "예상 결과",
                "tools_needed": ["필요한 도구들"],
                "dependencies": []
            }}
        ]
        """

        llm_result = await self.llm_agent.execute(plan_prompt, context, state)

        try:
            if isinstance(llm_result.data, list):
                return llm_result.data
            else:
                return json.loads(llm_result.data)
        except:
            # 기본 계획
            return [
                {
                    "step": 1,
                    "action": goal["primary_goal"],
                    "method": "직접 실행",
                    "expected_output": "목표 달성",
                    "tools_needed": [],
                    "dependencies": []
                }
            ]

    def _integrate_rpg_plan(self, original_plan: List[Dict[str, Any]], 
                           rpg_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """RPG 계획과 통합"""
        if not rpg_result or not rpg_result.get("rpg_graph"):
            return original_plan

        rpg_graph = rpg_result["rpg_graph"]
        execution_order = rpg_graph.get_execution_order()

        # RPG 노드를 계획 단계로 변환
        integrated_plan = []
        for i, node_id in enumerate(execution_order):
            if node_id in rpg_graph.nodes:
                node = rpg_graph.nodes[node_id]
                step = {
                    "step": i + 1,
                    "action": node.name,
                    "method": f"RPG 노드 실행: {node.description}",
                    "expected_output": f"{node.name} 완료",
                    "tools_needed": [],
                    "dependencies": node.inputs,
                    "rpg_node_id": node_id
                }
                integrated_plan.append(step)

        return integrated_plan if integrated_plan else original_plan

    async def _execute_plan(self, plan: List[Dict[str, Any]], context: Dict[str, Any], 
                           state: ComposableState) -> Dict[str, Any]:
        """계획 실행"""
        results = {"steps": [], "overall_success": True}

        for step in plan:
            step_result = await self._execute_step(step, context, state)
            results["steps"].append(step_result)

            # 실패시 전체 실행 중단 (선택적)
            if not step_result.get("success", True):
                results["overall_success"] = False
                if step.get("critical", True):
                    break

        return results

    async def _execute_step(self, step: Dict[str, Any], context: Dict[str, Any], 
                           state: ComposableState) -> Dict[str, Any]:
        """개별 단계 실행"""
        step_start = time.time()
        action_name = step.get("action", "Unknown")

        try:
            # 도구가 필요한 경우 도구 실행
            if step.get("tools_needed") and self.tool_executor:
                tool_results = []
                for tool_name in step["tools_needed"]:
                    tool_result = await self.tool_executor.execute_tool(tool_name)
                    tool_results.append(tool_result)

                step_result = {
                    "step": step["step"],
                    "action": action_name,
                    "success": all(tr.success for tr in tool_results),
                    "tool_results": [tr.to_dict() for tr in tool_results],
                    "execution_time": time.time() - step_start
                }
            else:
                # LLM 에이전트로 실행
                llm_result = await self.llm_agent.execute(
                    step["action"], context, state
                )

                step_result = {
                    "step": step["step"],
                    "action": action_name,
                    "success": llm_result.success,
                    "result": llm_result.data,
                    "reasoning": llm_result.reasoning,
                    "execution_time": time.time() - step_start
                }

            # 액션 히스토리에 추가
            self.action_history.append(action_name)

            return step_result

        except Exception as e:
            logger.error(f"단계 실행 오류: {action_name} - {str(e)}")
            return {
                "step": step["step"],
                "action": action_name,
                "success": False,
                "error": str(e),
                "execution_time": time.time() - step_start
            }

    async def _evaluate_results(self, goal: Dict[str, Any], results: Dict[str, Any], 
                               state: ComposableState) -> Dict[str, Any]:
        """결과 평가"""
        eval_prompt = f"""
        다음 목표와 실행 결과를 평가해주세요:

        목표: {json.dumps(goal, ensure_ascii=False, indent=2)}
        실행 결과: {json.dumps(results, ensure_ascii=False, indent=2)}

        평가 결과를 다음 JSON 형식으로 답변해주세요:
        {{
            "success": true/false,
            "achievement_rate": 0.0-1.0,
            "reasoning": "평가 근거",
            "retry_recommended": true/false,
            "improvements": ["개선 사항들"]
        }}
        """

        llm_result = await self.llm_agent.execute(eval_prompt, {}, state)

        try:
            if isinstance(llm_result.data, dict):
                return llm_result.data
            else:
                return json.loads(llm_result.data)
        except:
            # 기본 평가
            return {
                "success": results.get("overall_success", True),
                "achievement_rate": 1.0 if results.get("overall_success") else 0.5,
                "reasoning": "자동 평가 완료",
                "retry_recommended": False,
                "improvements": []
            }

    async def _improve_plan(self, original_plan: List[Dict[str, Any]], 
                           results: Dict[str, Any], evaluation: Dict[str, Any]) -> List[Dict[str, Any]]:
        """계획 개선"""
        # 실패한 단계들 식별 및 개선
        failed_steps = [step for step in results["steps"] if not step.get("success")]

        if not failed_steps:
            return original_plan

        # 개선된 계획 생성 (실제 구현에서는 더 정교한 로직 필요)
        improved_plan = original_plan.copy()

        for step in improved_plan:
            if step["step"] in [fs["step"] for fs in failed_steps]:
                step["method"] = f"개선된 방법: {step['method']}"
                step["retry"] = True

        return improved_plan

class CoordinatorAgent(BaseAgent):
    """조정 에이전트 - 다중 에이전트 조정"""

    def __init__(self, name: str = "coordinator_agent",
                 memory_manager: Optional[MemoryManager] = None,
                 tool_executor: Optional[ToolExecutor] = None):
        super().__init__(name, AgentType.COORDINATOR_AGENT, memory_manager, tool_executor)
        self.managed_agents: Dict[str, BaseAgent] = {}
        self.task_queue = []
        self.coordination_history = []

    def register_agent(self, agent: BaseAgent) -> bool:
        """에이전트 등록"""
        if agent.name in self.managed_agents:
            logger.warning(f"에이전트 이름 중복: {agent.name}")
            return False

        self.managed_agents[agent.name] = agent
        logger.info(f"에이전트 등록 완료: {agent.name}")
        return True

    async def execute(self, task: str, context: Dict[str, Any], 
                     state: ComposableState) -> AgentResult:
        """조정 에이전트 실행"""
        start_time = time.time()
        self.update_status(AgentStatus.THINKING)

        try:
            # 1. 작업 분석 및 분해
            subtasks = await self._decompose_task(task, context)

            # 2. 각 하위 작업에 적합한 에이전트 선택
            agent_assignments = self._assign_agents_to_tasks(subtasks, context)

            self.update_status(AgentStatus.ACTING)

            # 3. 에이전트들에게 작업 분산 실행
            execution_results = await self._coordinate_execution(agent_assignments, context, state)

            # 4. 결과 통합
            integrated_result = await self._integrate_results(execution_results, task, context)

            self.update_status(AgentStatus.IDLE)
            self.update_execution_stats()

            return AgentResult(
                success=True,
                data=integrated_result,
                reasoning="다중 에이전트 조정 완료",
                actions_taken=[f"coordinated_{len(agent_assignments)}_agents"],
                execution_time=time.time() - start_time,
                metadata={
                    "agents_used": list(agent_assignments.keys()),
                    "subtasks_count": len(subtasks)
                }
            )

        except Exception as e:
            self.update_status(AgentStatus.ERROR)
            logger.error(f"조정 에이전트 실행 오류: {str(e)}")

            return AgentResult(
                success=False,
                error=str(e),
                execution_time=time.time() - start_time
            )

    def can_handle_task(self, task: str, context: Dict[str, Any]) -> bool:
        """조정 처리 가능 여부 판단"""
        # 복잡하고 다단계이며 여러 에이전트가 필요한 작업
        coordination_indicators = [
            "종합", "전체", "통합", "조정", "관리", 
            "여러 단계", "복합", "다양한", "전반적"
        ]

        return (any(indicator in task for indicator in coordination_indicators) 
                and len(self.managed_agents) > 1)

    async def _decompose_task(self, task: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """작업 분해"""
        # 실제 구현에서는 더 정교한 작업 분해 로직 필요
        return [
            {
                "subtask": task,
                "priority": 1,
                "dependencies": [],
                "estimated_time": 60  # 초
            }
        ]

    def _assign_agents_to_tasks(self, subtasks: List[Dict[str, Any]], 
                               context: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
        """에이전트에게 작업 할당"""
        assignments = {}

        for subtask in subtasks:
            best_agent = None
            best_score = 0

            # 각 에이전트의 적합성 평가
            for agent_name, agent in self.managed_agents.items():
                if agent.status == AgentStatus.IDLE:
                    if agent.can_handle_task(subtask["subtask"], context):
                        score = self._calculate_agent_suitability(agent, subtask, context)
                        if score > best_score:
                            best_score = score
                            best_agent = agent_name

            # 에이전트 할당
            if best_agent:
                if best_agent not in assignments:
                    assignments[best_agent] = []
                assignments[best_agent].append(subtask)

        return assignments

    def _calculate_agent_suitability(self, agent: BaseAgent, subtask: Dict[str, Any], 
                                   context: Dict[str, Any]) -> float:
        """에이전트 적합성 점수 계산"""
        base_score = 0.5

        # 에이전트 타입별 가중치
        if agent.agent_type == AgentType.LLM_AGENT:
            if any(word in subtask["subtask"].lower() 
                  for word in ["분석", "생성", "분류"]):
                base_score += 0.3
        elif agent.agent_type == AgentType.AUTONOMOUS_AGENT:
            if "자동" in subtask["subtask"].lower():
                base_score += 0.3

        # 사용 빈도 역가중치 (로드 밸런싱)
        usage_penalty = min(0.2, agent.execution_count * 0.01)
        base_score -= usage_penalty

        return max(0.1, base_score)

    async def _coordinate_execution(self, assignments: Dict[str, List[Dict[str, Any]]], 
                                  context: Dict[str, Any], state: ComposableState) -> Dict[str, Any]:
        """조정된 실행"""
        results = {}

        # 병렬 실행 (asyncio.gather 사용)
        tasks = []
        agent_names = []

        for agent_name, subtasks in assignments.items():
            agent = self.managed_agents[agent_name]
            # 여러 하위 작업을 하나로 결합
            combined_task = " | ".join([st["subtask"] for st in subtasks])

            task_coroutine = agent.execute(combined_task, context, state)
            tasks.append(task_coroutine)
            agent_names.append(agent_name)

        # 병렬 실행
        if tasks:
            parallel_results = await asyncio.gather(*tasks, return_exceptions=True)

            for i, result in enumerate(parallel_results):
                agent_name = agent_names[i]
                if isinstance(result, Exception):
                    results[agent_name] = AgentResult(success=False, error=str(result))
                else:
                    results[agent_name] = result

        return results

    async def _integrate_results(self, results: Dict[str, Any], original_task: str, 
                               context: Dict[str, Any]) -> Dict[str, Any]:
        """결과 통합"""
        integrated = {
            "original_task": original_task,
            "agent_results": {},
            "success_count": 0,
            "total_agents": len(results),
            "overall_success": True,
            "combined_data": []
        }

        for agent_name, result in results.items():
            if isinstance(result, AgentResult):
                integrated["agent_results"][agent_name] = {
                    "success": result.success,
                    "data": result.data,
                    "reasoning": result.reasoning,
                    "execution_time": result.execution_time
                }

                if result.success:
                    integrated["success_count"] += 1
                    if result.data:
                        integrated["combined_data"].append(result.data)
                else:
                    integrated["overall_success"] = False

        # 성공률 계산
        integrated["success_rate"] = (integrated["success_count"] / 
                                    integrated["total_agents"] if integrated["total_agents"] > 0 else 0)

        return integrated

# 편의 함수들
def create_llm_agent(model_role: str = "gen", memory_manager: Optional[MemoryManager] = None, 
                    tool_executor: Optional[ToolExecutor] = None) -> LLMAgent:
    """LLM 에이전트 생성"""
    return LLMAgent(f"llm_{model_role}", model_role, memory_manager, tool_executor)

def create_autonomous_agent(memory_manager: Optional[MemoryManager] = None,
                          tool_executor: Optional[ToolExecutor] = None,
                          rpg_manager: Optional[RPGManager] = None) -> AutonomousAgent:
    """자율 에이전트 생성"""
    return AutonomousAgent("autonomous", memory_manager, tool_executor, rpg_manager)

def create_coordinator_agent(agents: List[BaseAgent] = None) -> CoordinatorAgent:
    """조정 에이전트 생성"""
    coordinator = CoordinatorAgent()

    if agents:
        for agent in agents:
            coordinator.register_agent(agent)

    return coordinator

def create_agent_system(memory_manager: MemoryManager, tool_executor: ToolExecutor, 
                       rpg_manager: RPGManager) -> CoordinatorAgent:
    """완전한 에이전트 시스템 생성"""
    # 개별 에이전트들 생성
    llm_gen = create_llm_agent("gen", memory_manager, tool_executor)
    llm_router1 = create_llm_agent("router1", memory_manager, tool_executor)
    llm_router2 = create_llm_agent("router2", memory_manager, tool_executor)
    autonomous = create_autonomous_agent(memory_manager, tool_executor, rpg_manager)

    # 조정 에이전트에 등록
    coordinator = create_coordinator_agent([llm_gen, llm_router1, llm_router2, autonomous])

    return coordinator

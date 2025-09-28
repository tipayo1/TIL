# utils.py와 router.py, graph.py를 한번에 생성하고 requirements.txt 업데이트
# utils.py - 공통 유틸리티
utils_py_content = '''# utils.py - 공통 유틸리티
# 프롬프트 템플릿 엔진, 설정 관리자, 로깅 및 모니터링

import os
import json
import logging
import time
from typing import Dict, List, Any, Optional, Union, TypeVar, Generic
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import asyncio
from datetime import datetime
import yaml

logger = logging.getLogger(__name__)

# LLM 생성 함수 (기존 코드 호환성)
def get_llm(model_role: str = "gen"):
    """
    LLM 인스턴스 생성
    model_role: gen, router1, router2 등
    """
    try:
        from langchain_openai import ChatOpenAI
        
        # 모델별 설정
        model_configs = {
            "gen": {"model": "gpt-4o-mini", "temperature": 0.1},
            "router1": {"model": "gpt-4o-mini", "temperature": 0.0},
            "router2": {"model": "gpt-4o-mini", "temperature": 0.0}
        }
        
        config = model_configs.get(model_role, model_configs["gen"])
        
        return ChatOpenAI(
            model=config["model"],
            temperature=config["temperature"],
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
    except Exception as e:
        logger.error(f"LLM 생성 실패: {model_role} - {str(e)}")
        raise

T = TypeVar('T')

class PromptTemplate:
    """프롬프트 템플릿 엔진"""
    
    def __init__(self, template: str, variables: Optional[List[str]] = None):
        self.template = template
        self.variables = variables or self._extract_variables()
        
    def format(self, **kwargs) -> str:
        """템플릿 포매팅"""
        try:
            # 누락된 변수에 대한 기본값 제공
            for var in self.variables:
                if var not in kwargs:
                    kwargs[var] = ""
            
            return self.template.format(**kwargs)
            
        except Exception as e:
            logger.error(f"프롬프트 템플릿 포매팅 실패: {str(e)}")
            return self.template
    
    def _extract_variables(self) -> List[str]:
        """템플릿에서 변수 추출"""
        import re
        variables = re.findall(r'\\{([^}]+)\\}', self.template)
        return list(set(variables))
    
    @classmethod
    def from_file(cls, file_path: str) -> 'PromptTemplate':
        """파일에서 템플릿 로드"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                template = f.read()
            return cls(template)
        except Exception as e:
            logger.error(f"프롬프트 템플릿 파일 로드 실패: {file_path} - {str(e)}")
            return cls("기본 템플릿: {content}")

class ConfigManager:
    """설정 관리자"""
    
    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = config_path
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """설정 파일 로드"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    if self.config_path.endswith('.yaml') or self.config_path.endswith('.yml'):
                        return yaml.safe_load(f)
                    else:
                        return json.load(f)
            else:
                return self._get_default_config()
                
        except Exception as e:
            logger.warning(f"설정 파일 로드 실패, 기본 설정 사용: {str(e)}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """기본 설정"""
        return {
            "system": {
                "log_level": "INFO",
                "max_memory_usage": "1GB",
                "max_execution_time": 300
            },
            "llm": {
                "default_model": "gpt-4o-mini",
                "temperature": 0.1,
                "max_tokens": 1000
            },
            "vector_db": {
                "default_type": "faiss",
                "embedding_model": "text-embedding-3-small",
                "chunk_size": 1000,
                "chunk_overlap": 200
            },
            "rpg": {
                "max_nodes": 50,
                "max_execution_time": 600,
                "enable_parallel_execution": True
            },
            "memory": {
                "short_term_size": 100,
                "short_term_ttl": 3600,
                "long_term_cache_size": 1000
            },
            "domains": {
                "hr": {
                    "index_name": "hr-rules",
                    "documents_path": "../data"
                },
                "general": {
                    "index_name": "general-docs",
                    "documents_path": "./docs"
                }
            }
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """설정값 조회 (점 표기법 지원)"""
        try:
            keys = key.split('.')
            value = self.config
            
            for k in keys:
                value = value[k]
            
            return value
            
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any) -> None:
        """설정값 업데이트"""
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def save(self) -> bool:
        """설정 파일 저장"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                if self.config_path.endswith('.yaml') or self.config_path.endswith('.yml'):
                    yaml.dump(self.config, f, default_flow_style=False, ensure_ascii=False)
                else:
                    json.dump(self.config, f, indent=2, ensure_ascii=False)
            
            logger.info(f"설정 파일 저장 완료: {self.config_path}")
            return True
            
        except Exception as e:
            logger.error(f"설정 파일 저장 실패: {str(e)}")
            return False

class MonitoringManager:
    """모니터링 및 로깅 관리자"""
    
    def __init__(self, log_level: str = "INFO"):
        self.metrics: Dict[str, Any] = {}
        self.execution_history: List[Dict[str, Any]] = []
        self.start_time = time.time()
        self._setup_logging(log_level)
    
    def _setup_logging(self, log_level: str):
        """로깅 설정"""
        logging.basicConfig(
            level=getattr(logging, log_level.upper()),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler('langgraph_rag.log', encoding='utf-8')
            ]
        )
    
    def record_execution(self, component: str, operation: str, 
                        duration: float, success: bool, **kwargs):
        """실행 기록"""
        record = {
            "timestamp": time.time(),
            "component": component,
            "operation": operation,
            "duration": duration,
            "success": success,
            "metadata": kwargs
        }
        
        self.execution_history.append(record)
        
        # 메트릭 업데이트
        metric_key = f"{component}_{operation}"
        if metric_key not in self.metrics:
            self.metrics[metric_key] = {
                "count": 0,
                "total_duration": 0.0,
                "success_count": 0,
                "error_count": 0
            }
        
        metric = self.metrics[metric_key]
        metric["count"] += 1
        metric["total_duration"] += duration
        
        if success:
            metric["success_count"] += 1
        else:
            metric["error_count"] += 1
    
    def get_metrics(self) -> Dict[str, Any]:
        """메트릭 조회"""
        processed_metrics = {}
        
        for key, metric in self.metrics.items():
            processed_metrics[key] = {
                **metric,
                "avg_duration": metric["total_duration"] / metric["count"] if metric["count"] > 0 else 0,
                "success_rate": metric["success_count"] / metric["count"] if metric["count"] > 0 else 0
            }
        
        return {
            "uptime": time.time() - self.start_time,
            "total_executions": len(self.execution_history),
            "component_metrics": processed_metrics
        }
    
    def get_recent_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """최근 실행 기록"""
        return self.execution_history[-limit:]

class CacheManager(Generic[T]):
    """캐시 관리자"""
    
    def __init__(self, max_size: int = 1000, ttl: int = 3600):
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.max_size = max_size
        self.ttl = ttl
        self.access_times: Dict[str, float] = {}
    
    def get(self, key: str) -> Optional[T]:
        """캐시에서 값 조회"""
        if key not in self.cache:
            return None
        
        entry = self.cache[key]
        
        # TTL 확인
        if time.time() - entry["timestamp"] > self.ttl:
            self._remove_key(key)
            return None
        
        # 접근 시간 업데이트
        self.access_times[key] = time.time()
        return entry["value"]
    
    def put(self, key: str, value: T) -> None:
        """캐시에 값 저장"""
        # 캐시 크기 관리
        while len(self.cache) >= self.max_size:
            self._evict_lru()
        
        self.cache[key] = {
            "value": value,
            "timestamp": time.time()
        }
        self.access_times[key] = time.time()
    
    def invalidate(self, key: str) -> bool:
        """캐시 무효화"""
        if key in self.cache:
            self._remove_key(key)
            return True
        return False
    
    def clear(self) -> None:
        """캐시 전체 삭제"""
        self.cache.clear()
        self.access_times.clear()
    
    def _remove_key(self, key: str) -> None:
        """키 삭제"""
        if key in self.cache:
            del self.cache[key]
        if key in self.access_times:
            del self.access_times[key]
    
    def _evict_lru(self) -> None:
        """LRU 제거"""
        if self.access_times:
            lru_key = min(self.access_times.keys(), 
                         key=lambda k: self.access_times[k])
            self._remove_key(lru_key)

class PerformanceProfiler:
    """성능 프로파일러"""
    
    def __init__(self):
        self.profiles: Dict[str, List[float]] = {}
        self.active_profiles: Dict[str, float] = {}
    
    def start_profile(self, name: str) -> None:
        """프로파일링 시작"""
        self.active_profiles[name] = time.time()
    
    def end_profile(self, name: str) -> Optional[float]:
        """프로파일링 종료"""
        if name not in self.active_profiles:
            return None
        
        duration = time.time() - self.active_profiles[name]
        del self.active_profiles[name]
        
        if name not in self.profiles:
            self.profiles[name] = []
        
        self.profiles[name].append(duration)
        return duration
    
    def get_profile_stats(self, name: str) -> Optional[Dict[str, float]]:
        """프로파일 통계"""
        if name not in self.profiles or not self.profiles[name]:
            return None
        
        durations = self.profiles[name]
        return {
            "count": len(durations),
            "total": sum(durations),
            "avg": sum(durations) / len(durations),
            "min": min(durations),
            "max": max(durations)
        }
    
    def context_profile(self, name: str):
        """컨텍스트 매니저로 사용"""
        return ProfileContext(self, name)

class ProfileContext:
    """프로파일링 컨텍스트 매니저"""
    
    def __init__(self, profiler: PerformanceProfiler, name: str):
        self.profiler = profiler
        self.name = name
    
    def __enter__(self):
        self.profiler.start_profile(self.name)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.profiler.end_profile(self.name)

# 전역 인스턴스들
_config_manager = ConfigManager()
_monitoring_manager = MonitoringManager()
_cache_manager = CacheManager()
_profiler = PerformanceProfiler()

# 편의 함수들
def get_config(key: str, default: Any = None) -> Any:
    """설정값 조회"""
    return _config_manager.get(key, default)

def set_config(key: str, value: Any) -> None:
    """설정값 업데이트"""
    _config_manager.set(key, value)

def save_config() -> bool:
    """설정 저장"""
    return _config_manager.save()

def record_execution(component: str, operation: str, duration: float, 
                    success: bool, **kwargs) -> None:
    """실행 기록"""
    _monitoring_manager.record_execution(component, operation, duration, success, **kwargs)

def get_metrics() -> Dict[str, Any]:
    """메트릭 조회"""
    return _monitoring_manager.get_metrics()

def cache_get(key: str) -> Optional[Any]:
    """캐시 조회"""
    return _cache_manager.get(key)

def cache_put(key: str, value: Any) -> None:
    """캐시 저장"""
    _cache_manager.put(key, value)

def profile(name: str):
    """성능 프로파일링 컨텍스트"""
    return _profiler.context_profile(name)

# 도메인별 설정 헬퍼
def get_domain_config(domain: str) -> Dict[str, Any]:
    """도메인별 설정 조회"""
    return get_config(f"domains.{domain}", {})

def get_vector_db_config() -> Dict[str, Any]:
    """벡터 DB 설정 조회"""
    return get_config("vector_db", {})

def get_llm_config() -> Dict[str, Any]:
    """LLM 설정 조회"""
    return get_config("llm", {})

# 오류 처리 데코레이터
def handle_errors(default_return=None, log_errors=True):
    """오류 처리 데코레이터"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if log_errors:
                    logger.error(f"{func.__name__} 실행 오류: {str(e)}")
                return default_return
        return wrapper
    return decorator

# 비동기 오류 처리 데코레이터
def handle_async_errors(default_return=None, log_errors=True):
    """비동기 오류 처리 데코레이터"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                if log_errors:
                    logger.error(f"{func.__name__} 비동기 실행 오류: {str(e)}")
                return default_return
        return wrapper
    return decorator
'''

# router.py - 지능형 라우팅
router_py_content = '''# router.py - 지능형 라우팅 시스템
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
'''

# 파일 저장
with open('utils.py', 'w', encoding='utf-8') as f:
    f.write(utils_py_content)

with open('router.py', 'w', encoding='utf-8') as f:
    f.write(router_py_content)

print("✅ utils.py 및 router.py 생성 완료")
print(f"utils.py 크기: {len(utils_py_content)} 문자")
print(f"router.py 크기: {len(router_py_content)} 문자")
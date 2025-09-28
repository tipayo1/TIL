# utils.py - 공통 유틸리티
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
        variables = re.findall(r'\{([^}]+)\}', self.template)
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

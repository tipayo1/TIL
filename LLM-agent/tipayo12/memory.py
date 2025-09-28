# memory.py - Agentic AI Memory 시스템
# LLM, Autonomy, Memory 구성 요소 중 Memory 전담

from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import json
import time
import asyncio
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class MemoryType(ABC):
    """메모리 타입 추상 기본 클래스"""

    @abstractmethod
    def store(self, key: str, value: Any, metadata: Optional[Dict] = None) -> bool:
        """메모리에 저장"""
        pass

    @abstractmethod
    def retrieve(self, key: str) -> Optional[Any]:
        """메모리에서 조회"""
        pass

    @abstractmethod
    def search(self, query: str, limit: int = 10) -> List[Tuple[str, Any, float]]:
        """메모리 검색"""
        pass

    @abstractmethod
    def clear(self) -> bool:
        """메모리 정리"""
        pass

@dataclass
class MemoryItem:
    """메모리 아이템"""
    key: str
    value: Any
    timestamp: float
    access_count: int = 0
    last_access: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)
    ttl: Optional[float] = None  # Time to live (초)

    def is_expired(self) -> bool:
        """만료 여부 확인"""
        if self.ttl is None:
            return False
        return time.time() - self.timestamp > self.ttl

    def update_access(self) -> None:
        """접근 정보 업데이트"""
        self.access_count += 1
        self.last_access = time.time()

class ShortTermMemory(MemoryType):
    """
    단기 메모리 - 현재 세션/대화 컨텍스트 관리
    - 빠른 접근 속도
    - 제한된 용량
    - 자동 만료
    """

    def __init__(self, max_items: int = 100, default_ttl: float = 3600):
        self.memory: Dict[str, MemoryItem] = {}
        self.max_items = max_items
        self.default_ttl = default_ttl
        self.access_order: List[str] = []  # LRU를 위한 접근 순서

    def store(self, key: str, value: Any, metadata: Optional[Dict] = None) -> bool:
        """단기 메모리에 저장"""
        try:
            # 기존 항목이 있으면 제거
            if key in self.memory:
                self.access_order.remove(key)

            # 용량 초과시 LRU 삭제
            while len(self.memory) >= self.max_items:
                self._evict_lru()

            # 새 항목 저장
            item = MemoryItem(
                key=key,
                value=value,
                timestamp=time.time(),
                metadata=metadata or {},
                ttl=self.default_ttl
            )

            self.memory[key] = item
            self.access_order.append(key)

            logger.debug(f"단기 메모리 저장: {key}")
            return True

        except Exception as e:
            logger.error(f"단기 메모리 저장 실패: {key} - {str(e)}")
            return False

    def retrieve(self, key: str) -> Optional[Any]:
        """단기 메모리에서 조회"""
        if key not in self.memory:
            return None

        item = self.memory[key]

        # 만료된 항목은 삭제
        if item.is_expired():
            self._remove_item(key)
            return None

        # 접근 정보 업데이트
        item.update_access()
        self._move_to_end(key)

        logger.debug(f"단기 메모리 조회: {key}")
        return item.value

    def search(self, query: str, limit: int = 10) -> List[Tuple[str, Any, float]]:
        """단기 메모리 검색 (키 매칭 기반)"""
        results = []
        query_lower = query.lower()

        for key, item in self.memory.items():
            if item.is_expired():
                continue

            # 단순 키워드 매칭 점수
            if query_lower in key.lower():
                score = 1.0
            elif any(query_lower in str(v).lower() 
                    for v in item.metadata.values()):
                score = 0.8
            elif query_lower in str(item.value).lower():
                score = 0.6
            else:
                continue

            results.append((key, item.value, score))

        # 점수순으로 정렬하고 제한
        results.sort(key=lambda x: x[2], reverse=True)
        return results[:limit]

    def clear(self) -> bool:
        """단기 메모리 전체 정리"""
        self.memory.clear()
        self.access_order.clear()
        logger.info("단기 메모리 정리 완료")
        return True

    def cleanup_expired(self) -> int:
        """만료된 항목들 정리"""
        expired_keys = []
        for key, item in self.memory.items():
            if item.is_expired():
                expired_keys.append(key)

        for key in expired_keys:
            self._remove_item(key)

        if expired_keys:
            logger.info(f"만료된 단기 메모리 {len(expired_keys)}개 정리")

        return len(expired_keys)

    def get_context_window(self, window_size: int = 10) -> List[Tuple[str, Any]]:
        """최근 컨텍스트 윈도우 반환"""
        recent_keys = self.access_order[-window_size:]
        context = []

        for key in recent_keys:
            if key in self.memory and not self.memory[key].is_expired():
                context.append((key, self.memory[key].value))

        return context

    def _evict_lru(self) -> None:
        """LRU 항목 제거"""
        if self.access_order:
            lru_key = self.access_order[0]
            self._remove_item(lru_key)

    def _remove_item(self, key: str) -> None:
        """항목 제거"""
        if key in self.memory:
            del self.memory[key]
        if key in self.access_order:
            self.access_order.remove(key)

    def _move_to_end(self, key: str) -> None:
        """접근 순서를 끝으로 이동"""
        if key in self.access_order:
            self.access_order.remove(key)
            self.access_order.append(key)

class LongTermMemory(MemoryType):
    """
    장기 메모리 - 벡터 저장소 연동 지속적 지식 관리
    - 대용량 저장
    - 의미적 검색 
    - 영구 보존
    """

    def __init__(self, vector_store=None, embedding_model=None):
        self.vector_store = vector_store
        self.embedding_model = embedding_model
        self.local_cache: Dict[str, MemoryItem] = {}  # 빠른 접근을 위한 로컬 캐시
        self.cache_limit = 1000

    def store(self, key: str, value: Any, metadata: Optional[Dict] = None) -> bool:
        """장기 메모리에 저장"""
        try:
            # 로컬 캐시에 저장
            item = MemoryItem(
                key=key,
                value=value,
                timestamp=time.time(),
                metadata=metadata or {}
            )

            # 캐시 크기 관리
            if len(self.local_cache) >= self.cache_limit:
                self._evict_cache_lru()

            self.local_cache[key] = item

            # 벡터 저장소가 있으면 비동기로 저장
            if self.vector_store and self.embedding_model:
                # 실제 구현에서는 asyncio.create_task() 사용
                self._store_to_vector_db(key, value, metadata)

            logger.debug(f"장기 메모리 저장: {key}")
            return True

        except Exception as e:
            logger.error(f"장기 메모리 저장 실패: {key} - {str(e)}")
            return False

    def retrieve(self, key: str) -> Optional[Any]:
        """장기 메모리에서 조회"""
        # 먼저 로컬 캐시 확인
        if key in self.local_cache:
            item = self.local_cache[key]
            item.update_access()
            logger.debug(f"장기 메모리 캐시 조회: {key}")
            return item.value

        # 벡터 저장소에서 검색
        if self.vector_store:
            result = self._retrieve_from_vector_db(key)
            if result:
                # 캐시에 저장
                self.local_cache[key] = MemoryItem(
                    key=key,
                    value=result,
                    timestamp=time.time()
                )
                logger.debug(f"장기 메모리 벡터DB 조회: {key}")
                return result

        return None

    def search(self, query: str, limit: int = 10) -> List[Tuple[str, Any, float]]:
        """장기 메모리 의미적 검색"""
        results = []

        # 로컬 캐시에서 키워드 검색
        query_lower = query.lower()
        for key, item in self.local_cache.items():
            if query_lower in key.lower() or query_lower in str(item.value).lower():
                score = 0.8  # 캐시는 높은 점수
                results.append((key, item.value, score))

        # 벡터 저장소에서 의미적 검색
        if self.vector_store and self.embedding_model:
            vector_results = self._search_vector_db(query, limit)
            results.extend(vector_results)

        # 중복 제거 및 점수 정렬
        unique_results = {}
        for key, value, score in results:
            if key not in unique_results or unique_results[key][1] < score:
                unique_results[key] = (value, score)

        final_results = [(k, v[0], v[1]) for k, v in unique_results.items()]
        final_results.sort(key=lambda x: x[2], reverse=True)

        return final_results[:limit]

    def clear(self) -> bool:
        """장기 메모리 정리 (캐시만)"""
        self.local_cache.clear()
        logger.info("장기 메모리 캐시 정리 완료")
        return True

    def _store_to_vector_db(self, key: str, value: Any, metadata: Dict) -> None:
        """벡터 DB에 저장 (실제 구현에서는 비동기)"""
        # 실제 벡터 저장소 연동 로직
        pass

    def _retrieve_from_vector_db(self, key: str) -> Optional[Any]:
        """벡터 DB에서 조회"""
        # 실제 벡터 저장소 조회 로직
        return None

    def _search_vector_db(self, query: str, limit: int) -> List[Tuple[str, Any, float]]:
        """벡터 DB 의미적 검색"""
        # 실제 벡터 검색 로직
        return []

    def _evict_cache_lru(self) -> None:
        """캐시 LRU 제거"""
        if self.local_cache:
            # 가장 오래된 항목 제거
            oldest_key = min(self.local_cache.keys(), 
                           key=lambda k: self.local_cache[k].last_access)
            del self.local_cache[oldest_key]

class MemoryRetriever:
    """메모리 검색 통합 인터페이스"""

    def __init__(self, short_term: ShortTermMemory, long_term: LongTermMemory):
        self.short_term = short_term
        self.long_term = long_term

    def search_all(self, query: str, limit: int = 20) -> List[Tuple[str, Any, float, str]]:
        """단기/장기 메모리 통합 검색"""
        results = []

        # 단기 메모리 검색 (높은 가중치)
        short_results = self.short_term.search(query, limit//2)
        for key, value, score in short_results:
            results.append((key, value, score * 1.2, "short_term"))  # 단기 메모리 가중치

        # 장기 메모리 검색
        long_results = self.long_term.search(query, limit//2)
        for key, value, score in long_results:
            results.append((key, value, score, "long_term"))

        # 점수순 정렬
        results.sort(key=lambda x: x[2], reverse=True)
        return results[:limit]

    def get_relevant_context(self, query: str, context_size: int = 5) -> Dict[str, Any]:
        """관련 컨텍스트 조회"""
        search_results = self.search_all(query, context_size * 2)

        context = {
            "query": query,
            "timestamp": time.time(),
            "short_term_items": [],
            "long_term_items": [],
            "total_items": len(search_results)
        }

        for key, value, score, memory_type in search_results:
            item = {"key": key, "value": value, "score": score}
            if memory_type == "short_term":
                context["short_term_items"].append(item)
            else:
                context["long_term_items"].append(item)

        return context

class MemoryManager:
    """메모리 시스템 통합 관리자"""

    def __init__(self, vector_store=None, embedding_model=None, 
                 short_term_config: Optional[Dict] = None):

        # 단기 메모리 초기화
        st_config = short_term_config or {}
        self.short_term = ShortTermMemory(
            max_items=st_config.get("max_items", 100),
            default_ttl=st_config.get("default_ttl", 3600)
        )

        # 장기 메모리 초기화
        self.long_term = LongTermMemory(vector_store, embedding_model)

        # 검색 인터페이스
        self.retriever = MemoryRetriever(self.short_term, self.long_term)

        # 자동 정리 설정
        self.cleanup_interval = 300  # 5분
        self.last_cleanup = time.time()

    def store(self, key: str, value: Any, memory_type: str = "short_term", 
              metadata: Optional[Dict] = None) -> bool:
        """메모리에 저장"""
        if memory_type == "short_term":
            return self.short_term.store(key, value, metadata)
        elif memory_type == "long_term":
            return self.long_term.store(key, value, metadata)
        elif memory_type == "both":
            # 양쪽 모두에 저장
            short_success = self.short_term.store(key, value, metadata)
            long_success = self.long_term.store(key, value, metadata)
            return short_success and long_success
        else:
            raise ValueError(f"Unknown memory_type: {memory_type}")

    def retrieve(self, key: str, memory_type: str = "both") -> Optional[Any]:
        """메모리에서 조회"""
        if memory_type == "short_term":
            return self.short_term.retrieve(key)
        elif memory_type == "long_term":
            return self.long_term.retrieve(key)
        elif memory_type == "both":
            # 단기 메모리 우선 조회
            result = self.short_term.retrieve(key)
            if result is None:
                result = self.long_term.retrieve(key)
            return result
        else:
            raise ValueError(f"Unknown memory_type: {memory_type}")

    def search(self, query: str, limit: int = 10) -> List[Tuple[str, Any, float, str]]:
        """통합 메모리 검색"""
        return self.retriever.search_all(query, limit)

    def get_context(self, query: str, context_size: int = 5) -> Dict[str, Any]:
        """관련 컨텍스트 조회"""
        return self.retriever.get_relevant_context(query, context_size)

    def cleanup(self) -> Dict[str, int]:
        """메모리 정리"""
        short_cleaned = self.short_term.cleanup_expired()
        self.last_cleanup = time.time()

        return {
            "short_term_cleaned": short_cleaned,
            "timestamp": self.last_cleanup
        }

    def auto_cleanup_if_needed(self) -> Optional[Dict[str, int]]:
        """필요시 자동 정리"""
        if time.time() - self.last_cleanup > self.cleanup_interval:
            return self.cleanup()
        return None

    def get_memory_stats(self) -> Dict[str, Any]:
        """메모리 사용 통계"""
        return {
            "short_term": {
                "total_items": len(self.short_term.memory),
                "max_items": self.short_term.max_items,
                "usage_ratio": len(self.short_term.memory) / self.short_term.max_items
            },
            "long_term": {
                "cached_items": len(self.long_term.local_cache),
                "cache_limit": self.long_term.cache_limit
            },
            "last_cleanup": self.last_cleanup,
            "cleanup_interval": self.cleanup_interval
        }

    def migrate_to_long_term(self, key_pattern: str = None, 
                            access_threshold: int = 3) -> int:
        """단기 메모리에서 장기 메모리로 이주"""
        migrated = 0
        keys_to_migrate = []

        for key, item in self.short_term.memory.items():
            # 패턴 매칭 또는 접근 횟수 기반 선택
            should_migrate = False

            if key_pattern and key_pattern in key:
                should_migrate = True
            elif item.access_count >= access_threshold:
                should_migrate = True

            if should_migrate:
                keys_to_migrate.append(key)

        # 이주 실행
        for key in keys_to_migrate:
            item = self.short_term.memory[key]
            if self.long_term.store(key, item.value, item.metadata):
                migrated += 1
                logger.info(f"메모리 이주: {key} (접근횟수: {item.access_count})")

        return migrated

# 편의 함수들
def create_memory_manager(vector_store=None, embedding_model=None) -> MemoryManager:
    """메모리 매니저 생성 헬퍼"""
    return MemoryManager(vector_store, embedding_model)

def create_lightweight_memory() -> MemoryManager:
    """경량 메모리 매니저 생성 (벡터 저장소 없이)"""
    return MemoryManager()

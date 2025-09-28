"""
memory.py - AI 에이전트 메모리 관리 모듈

Agentic AI의 핵심 구성요소인 Memory를 구현:
- 장기 메모리: 사용자 패턴, 성공적인 워크플로우 학습
- 단기 메모리: 현재 세션 컨텍스트, 진행 상태
- 벤더 중립적 메모리 백엔드 지원
- RPG와 통합된 컨텍스트 인식 메모리
"""

import json
import logging
from typing import Dict, List, Optional, Any, Union, Protocol
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from abc import ABC, abstractmethod
from enum import Enum
import hashlib
import pickle


class MemoryType(Enum):
    """메모리 타입 정의"""
    SHORT_TERM = "short_term"    # 단기 메모리 (세션 내)
    LONG_TERM = "long_term"      # 장기 메모리 (지속적)
    WORKING = "working"          # 작업 메모리 (현재 작업용)
    EPISODIC = "episodic"        # 에피소드 메모리 (경험 기반)


@dataclass
class MemoryEntry:
    """메모리 항목 클래스"""
    id: str
    content: Any
    memory_type: MemoryType
    created_at: datetime = field(default_factory=datetime.now)
    last_accessed: datetime = field(default_factory=datetime.now)
    access_count: int = 0
    importance_score: float = 1.0
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class MemoryBackend(Protocol):
    """메모리 백엔드 인터페이스"""

    def store(self, entry: MemoryEntry) -> bool:
        """메모리 항목 저장"""
        ...

    def retrieve(self, memory_id: str) -> Optional[MemoryEntry]:
        """메모리 항목 조회"""
        ...

    def search(self, query: str, memory_type: Optional[MemoryType] = None, 
               limit: int = 10) -> List[MemoryEntry]:
        """메모리 검색"""
        ...

    def delete(self, memory_id: str) -> bool:
        """메모리 항목 삭제"""
        ...

    def cleanup(self, retention_days: int = 30) -> int:
        """오래된 메모리 정리"""
        ...


class InMemoryBackend:
    """인메모리 백엔드 (개발/테스트용)"""

    def __init__(self):
        self.storage: Dict[str, MemoryEntry] = {}
        self.logger = logging.getLogger(__name__)

    def store(self, entry: MemoryEntry) -> bool:
        try:
            self.storage[entry.id] = entry
            return True
        except Exception as e:
            self.logger.error(f"메모리 저장 실패: {e}")
            return False

    def retrieve(self, memory_id: str) -> Optional[MemoryEntry]:
        entry = self.storage.get(memory_id)
        if entry:
            entry.last_accessed = datetime.now()
            entry.access_count += 1
        return entry

    def search(self, query: str, memory_type: Optional[MemoryType] = None, 
               limit: int = 10) -> List[MemoryEntry]:
        results = []
        query_lower = query.lower()

        for entry in self.storage.values():
            # 타입 필터
            if memory_type and entry.memory_type != memory_type:
                continue

            # 간단한 텍스트 검색 (실제로는 더 정교한 검색 필요)
            content_str = str(entry.content).lower()
            if query_lower in content_str or any(query_lower in tag for tag in entry.tags):
                results.append(entry)

        # 중요도와 최근 접근 시간으로 정렬
        results.sort(key=lambda x: (x.importance_score, x.last_accessed), reverse=True)
        return results[:limit]

    def delete(self, memory_id: str) -> bool:
        return self.storage.pop(memory_id, None) is not None

    def cleanup(self, retention_days: int = 30) -> int:
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        deleted_count = 0

        to_delete = [
            mem_id for mem_id, entry in self.storage.items()
            if entry.memory_type == MemoryType.SHORT_TERM and entry.last_accessed < cutoff_date
        ]

        for mem_id in to_delete:
            self.delete(mem_id)
            deleted_count += 1

        return deleted_count


class VectorMemoryBackend:
    """벡터 기반 메모리 백엔드 (의미적 검색 지원)"""

    def __init__(self, vector_store=None, embedding_model=None):
        self.vector_store = vector_store  # 외부 벡터 DB 연동
        self.embedding_model = embedding_model
        self.fallback_backend = InMemoryBackend()
        self.logger = logging.getLogger(__name__)

    def store(self, entry: MemoryEntry) -> bool:
        # 벡터 저장소와 폴백 저장소 모두에 저장
        success = self.fallback_backend.store(entry)

        if self.vector_store and self._is_vectorizable(entry):
            try:
                # 벡터 저장 로직 (실제 구현시 embedding 생성 필요)
                pass
            except Exception as e:
                self.logger.warning(f"벡터 저장 실패, 폴백 사용: {e}")

        return success

    def search(self, query: str, memory_type: Optional[MemoryType] = None, 
               limit: int = 10) -> List[MemoryEntry]:
        # 벡터 검색 + 키워드 검색 조합
        vector_results = []

        if self.vector_store and self.embedding_model:
            try:
                # 의미적 검색 수행 (실제 구현시 embedding 필요)
                pass
            except Exception as e:
                self.logger.warning(f"벡터 검색 실패, 폴백 사용: {e}")

        # 폴백 검색
        keyword_results = self.fallback_backend.search(query, memory_type, limit)

        # 결과 병합 및 중복 제거
        all_results = vector_results + keyword_results
        unique_results = {entry.id: entry for entry in all_results}

        return list(unique_results.values())[:limit]

    def retrieve(self, memory_id: str) -> Optional[MemoryEntry]:
        return self.fallback_backend.retrieve(memory_id)

    def delete(self, memory_id: str) -> bool:
        return self.fallback_backend.delete(memory_id)

    def cleanup(self, retention_days: int = 30) -> int:
        return self.fallback_backend.cleanup(retention_days)

    def _is_vectorizable(self, entry: MemoryEntry) -> bool:
        """항목이 벡터화 가능한지 확인"""
        return isinstance(entry.content, str) and len(entry.content) > 10


class AgentMemoryManager:
    """AI 에이전트 메모리 매니저"""

    def __init__(self, backend: Optional[MemoryBackend] = None, 
                 config: Optional[Dict] = None):
        self.backend = backend or InMemoryBackend()
        self.config = config or {}
        self.logger = logging.getLogger(__name__)

        # 메모리 관리 설정
        self.short_term_ttl = self.config.get("short_term_ttl", 3600)  # 1시간
        self.working_memory_limit = self.config.get("working_memory_limit", 50)
        self.importance_threshold = self.config.get("importance_threshold", 0.7)

    def remember(self, content: Any, memory_type: MemoryType = MemoryType.WORKING,
                 importance: float = 1.0, tags: Optional[List[str]] = None) -> str:
        """메모리에 정보 저장"""

        # 메모리 ID 생성
        content_str = str(content) + str(datetime.now())
        memory_id = hashlib.md5(content_str.encode()).hexdigest()

        entry = MemoryEntry(
            id=memory_id,
            content=content,
            memory_type=memory_type,
            importance_score=importance,
            tags=tags or [],
            metadata={
                "session_id": self._get_current_session_id(),
                "user_id": self._get_current_user_id()
            }
        )

        success = self.backend.store(entry)
        if success:
            self.logger.debug(f"메모리 저장 성공: {memory_id[:8]}...")

            # 작업 메모리 제한 관리
            if memory_type == MemoryType.WORKING:
                self._manage_working_memory_limit()

        return memory_id

    def recall(self, memory_id: str) -> Optional[Any]:
        """특정 메모리 회상"""
        entry = self.backend.retrieve(memory_id)
        return entry.content if entry else None

    def search_memories(self, query: str, memory_type: Optional[MemoryType] = None,
                       limit: int = 10) -> List[Dict[str, Any]]:
        """메모리 검색"""
        entries = self.backend.search(query, memory_type, limit)

        return [{
            "id": entry.id,
            "content": entry.content,
            "type": entry.memory_type.value,
            "importance": entry.importance_score,
            "created_at": entry.created_at.isoformat(),
            "tags": entry.tags
        } for entry in entries]

    def forget(self, memory_id: str) -> bool:
        """메모리 삭제"""
        return self.backend.delete(memory_id)

    def get_context(self, query: str, max_entries: int = 5) -> Dict[str, Any]:
        """쿼리 관련 컨텍스트 메모리 수집"""

        # 관련 메모리들 검색
        relevant_memories = self.search_memories(query, limit=max_entries)

        # 현재 세션의 작업 메모리
        working_memories = self.search_memories(
            query, MemoryType.WORKING, limit=3
        )

        # 장기 메모리에서 패턴 검색
        pattern_memories = self.search_memories(
            query, MemoryType.LONG_TERM, limit=2
        )

        context = {
            "query": query,
            "relevant_memories": relevant_memories,
            "working_context": working_memories,
            "learned_patterns": pattern_memories,
            "context_summary": self._summarize_context(relevant_memories)
        }

        return context

    def learn_from_success(self, workflow_info: Dict[str, Any], 
                          outcome_score: float):
        """성공적인 워크플로우로부터 학습"""

        if outcome_score > self.importance_threshold:
            # 성공 패턴을 장기 메모리에 저장
            pattern_content = {
                "workflow": workflow_info,
                "outcome_score": outcome_score,
                "learned_at": datetime.now(),
                "pattern_type": "successful_workflow"
            }

            self.remember(
                content=pattern_content,
                memory_type=MemoryType.LONG_TERM,
                importance=outcome_score,
                tags=["workflow_pattern", "success", "learning"]
            )

            self.logger.info(f"워크플로우 학습 완료 (점수: {outcome_score})")

    def get_user_preferences(self, user_id: str) -> Dict[str, Any]:
        """사용자별 선호도 정보 조회"""
        user_memories = self.backend.search(
            f"user:{user_id}", 
            MemoryType.LONG_TERM,
            limit=20
        )

        preferences = {
            "preferred_response_style": "detailed",  # 기본값
            "frequent_topics": [],
            "successful_patterns": [],
            "last_interactions": []
        }

        for memory in user_memories:
            content = memory.content
            if isinstance(content, dict):
                if "user_preference" in content:
                    preferences.update(content["user_preference"])
                elif "successful_workflow" in content:
                    preferences["successful_patterns"].append(content)

        return preferences

    def update_user_preference(self, user_id: str, preference_key: str, 
                             preference_value: Any):
        """사용자 선호도 업데이트"""
        preference_content = {
            "user_preference": {preference_key: preference_value},
            "user_id": user_id,
            "updated_at": datetime.now()
        }

        self.remember(
            content=preference_content,
            memory_type=MemoryType.LONG_TERM,
            importance=0.8,
            tags=["user_preference", f"user:{user_id}"]
        )

    def cleanup_old_memories(self, retention_days: int = 30) -> int:
        """오래된 메모리 정리"""
        return self.backend.cleanup(retention_days)

    def _manage_working_memory_limit(self):
        """작업 메모리 제한 관리"""
        working_memories = self.backend.search(
            "", MemoryType.WORKING, limit=self.working_memory_limit + 10
        )

        if len(working_memories) > self.working_memory_limit:
            # 중요도가 낮고 오래된 것들 삭제
            to_delete = sorted(
                working_memories,
                key=lambda x: (x.importance_score, x.last_accessed)
            )[:(len(working_memories) - self.working_memory_limit)]

            for memory in to_delete:
                self.backend.delete(memory.id)

    def _summarize_context(self, memories: List[Dict]) -> str:
        """컨텍스트 메모리들을 요약"""
        if not memories:
            return "관련 컨텍스트 없음"

        # 간단한 요약 (실제로는 LLM 활용)
        topics = set()
        for memory in memories:
            topics.update(memory.get("tags", []))

        return f"관련 주제들: {', '.join(list(topics)[:5])}"

    def _get_current_session_id(self) -> str:
        """현재 세션 ID 반환 (실제 구현 필요)"""
        return "default_session"

    def _get_current_user_id(self) -> str:
        """현재 사용자 ID 반환 (실제 구현 필요)"""
        return "default_user"


# 유틸리티 함수들
def create_memory_manager(backend_type: str = "inmemory", 
                         config: Optional[Dict] = None) -> AgentMemoryManager:
    """메모리 매니저 팩토리 함수"""

    if backend_type == "inmemory":
        backend = InMemoryBackend()
    elif backend_type == "vector":
        backend = VectorMemoryBackend()
    else:
        raise ValueError(f"지원하지 않는 백엔드 타입: {backend_type}")

    return AgentMemoryManager(backend, config)


def memory_context_decorator(memory_manager: AgentMemoryManager):
    """메모리 컨텍스트를 자동으로 주입하는 데코레이터"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # 함수 호출 전 컨텍스트 수집
            if "query" in kwargs or (args and isinstance(args[0], str)):
                query = kwargs.get("query", args[0] if args else "")
                context = memory_manager.get_context(query)
                kwargs["memory_context"] = context

            result = func(*args, **kwargs)

            # 함수 호출 후 결과를 메모리에 저장
            if result and "success" in str(result):
                memory_manager.remember(
                    content={"function": func.__name__, "result": result},
                    memory_type=MemoryType.WORKING,
                    tags=["function_result"]
                )

            return result
        return wrapper
    return decorator

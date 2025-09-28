# state.py - 통합 상태 관리 시스템

from typing import Dict, List, Any, Optional, Union, TypedDict
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from langgraph.graph import MessagesState
from langchain_core.documents import Document
import asyncio
import json

# RPG 그래프 상태 구조
@dataclass 
class RPGNodeState:
    """RPG 노드 상태 정보"""
    node_id: str
    node_type: str  # capability, file, function, dependency
    status: str     # planned, in_progress, completed, failed
    metadata: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    outputs: List[str] = field(default_factory=list)

@dataclass
class RPGGraphState:
    """RPG 그래프 전체 상태"""
    nodes: Dict[str, RPGNodeState] = field(default_factory=dict)
    edges: List[Dict[str, str]] = field(default_factory=list)
    execution_plan: List[str] = field(default_factory=list)
    current_phase: str = "planning"  # planning, execution, validation

# 메모리 상태 구조  
@dataclass
class MemoryState:
    """메모리 시스템 상태"""
    short_term: Dict[str, Any] = field(default_factory=dict)
    long_term_refs: List[str] = field(default_factory=list) 
    context_window: List[str] = field(default_factory=list)
    memory_usage: float = 0.0

# 도구 상태 구조
@dataclass  
class ToolState:
    """도구 시스템 상태"""
    available_tools: Dict[str, Any] = field(default_factory=dict)
    active_tools: List[str] = field(default_factory=list)
    tool_outputs: Dict[str, Any] = field(default_factory=dict)

class ComposableState(MessagesState, total=False):
    """
    Composable한 통합 상태 클래스
    - RPG 상태 관리
    - 메모리 시스템 연동  
    - 도구 상태 추적
    - 동적 상태 확장
    """

    # === Core State ===
    user_question: str
    refined_question: str

    # === RPG State ===
    rpg_graph: RPGGraphState
    current_capability: Optional[str]
    execution_path: List[str]

    # === Memory State ===
    memory_state: MemoryState

    # === Tool State ===
    tool_state: ToolState

    # === Legacy RAG State (하위 호환) ===
    retrieved_docs: List[Document]
    is_hr_question: bool
    is_rag_suitable: bool
    department_info: Optional[Dict[str, str]]
    verification: str
    answer_type: str
    final_answer: str

    # === Dynamic Extensions ===
    extensions: Dict[str, Any] = field(default_factory=dict)

    def update_rpg_node(self, node_id: str, status: str, **kwargs):
        """RPG 노드 상태 업데이트"""
        if not hasattr(self, 'rpg_graph') or not self.rpg_graph:
            self.rpg_graph = RPGGraphState()

        if node_id in self.rpg_graph.nodes:
            self.rpg_graph.nodes[node_id].status = status
            self.rpg_graph.nodes[node_id].metadata.update(kwargs)

    def add_memory(self, key: str, value: Any, memory_type: str = "short_term"):
        """메모리 추가"""
        if not hasattr(self, 'memory_state') or not self.memory_state:
            self.memory_state = MemoryState()

        if memory_type == "short_term":
            self.memory_state.short_term[key] = value
        elif memory_type == "long_term":
            self.memory_state.long_term_refs.append(key)

    def register_tool(self, tool_name: str, tool_instance: Any):
        """도구 등록"""
        if not hasattr(self, 'tool_state') or not self.tool_state:
            self.tool_state = ToolState()

        self.tool_state.available_tools[tool_name] = tool_instance

    def get_context_summary(self) -> Dict[str, Any]:
        """현재 상태의 컨텍스트 요약"""
        return {
            "question": getattr(self, 'refined_question', ''),
            "current_phase": getattr(self.rpg_graph, 'current_phase', 'none') if hasattr(self, 'rpg_graph') else 'none',
            "memory_items": len(self.memory_state.short_term) if hasattr(self, 'memory_state') else 0,
            "available_tools": list(self.tool_state.available_tools.keys()) if hasattr(self, 'tool_state') else [],
            "answer_type": getattr(self, 'answer_type', 'pending')
        }

# State 편의 함수들
def create_initial_state(user_question: str) -> ComposableState:
    """초기 상태 생성"""
    return ComposableState(
        user_question=user_question,
        refined_question="",
        rpg_graph=RPGGraphState(),
        memory_state=MemoryState(), 
        tool_state=ToolState(),
        retrieved_docs=[],
        is_hr_question=False,
        is_rag_suitable=False,
        department_info=None,
        verification="",
        answer_type="pending",
        final_answer="",
        current_capability=None,
        execution_path=[],
        extensions={}
    )

# 타입 별칭
State = ComposableState

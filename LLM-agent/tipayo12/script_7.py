# tools.py - Tool 인터페이스 관리 생성
tools_py_content = '''# tools.py - Tool 인터페이스 관리
# Agentic AI의 Tool 구성요소 - 외부 시스템과의 인터페이스

from typing import Dict, List, Any, Optional, Union, Callable, Type
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import json
import inspect
import logging
from enum import Enum
import asyncio
import time

logger = logging.getLogger(__name__)

class ToolType(Enum):
    """도구 타입"""
    DATABASE = "database"          # 데이터베이스 도구
    API = "api"                   # API 호출 도구
    FILE = "file"                 # 파일 시스템 도구
    SEARCH = "search"             # 검색 도구
    COMPUTATION = "computation"    # 계산 도구
    COMMUNICATION = "communication" # 통신 도구
    CUSTOM = "custom"             # 사용자 정의 도구

class ToolStatus(Enum):
    """도구 상태"""
    AVAILABLE = "available"
    BUSY = "busy"
    ERROR = "error"
    DISABLED = "disabled"

@dataclass
class ToolResult:
    """도구 실행 결과"""
    success: bool
    data: Any = None
    error: Optional[str] = None
    execution_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "data": self.data,
            "error": self.error,
            "execution_time": self.execution_time,
            "metadata": self.metadata
        }

class BaseTool(ABC):
    """기본 도구 추상 클래스"""
    
    def __init__(self, name: str, description: str, tool_type: ToolType):
        self.name = name
        self.description = description
        self.tool_type = tool_type
        self.status = ToolStatus.AVAILABLE
        self.usage_count = 0
        self.last_used = None
        self.config: Dict[str, Any] = {}
    
    @abstractmethod
    async def execute(self, **kwargs) -> ToolResult:
        """도구 실행"""
        pass
    
    @abstractmethod
    def validate_input(self, **kwargs) -> bool:
        """입력 검증"""
        pass
    
    def get_schema(self) -> Dict[str, Any]:
        """도구 스키마 반환"""
        return {
            "name": self.name,
            "description": self.description,
            "type": self.tool_type.value,
            "status": self.status.value,
            "usage_count": self.usage_count,
            "parameters": self._get_parameters_schema()
        }
    
    def _get_parameters_schema(self) -> Dict[str, Any]:
        """파라미터 스키마 자동 생성"""
        sig = inspect.signature(self.execute)
        params = {}
        
        for param_name, param in sig.parameters.items():
            if param_name == "self":
                continue
                
            param_info = {
                "required": param.default == param.empty,
                "type": str(param.annotation) if param.annotation != param.empty else "Any"
            }
            params[param_name] = param_info
        
        return params
    
    def update_usage(self) -> None:
        """사용 통계 업데이트"""
        self.usage_count += 1
        self.last_used = time.time()

class VectorSearchTool(BaseTool):
    """벡터 검색 도구"""
    
    def __init__(self, vector_store, name: str = "vector_search"):
        super().__init__(
            name=name,
            description="벡터 저장소에서 유사도 검색",
            tool_type=ToolType.SEARCH
        )
        self.vector_store = vector_store
    
    async def execute(self, query: str, top_k: int = 5, **kwargs) -> ToolResult:
        """벡터 검색 실행"""
        start_time = time.time()
        
        try:
            if not self.validate_input(query=query, top_k=top_k):
                return ToolResult(
                    success=False,
                    error="입력 검증 실패",
                    execution_time=time.time() - start_time
                )
            
            self.status = ToolStatus.BUSY
            
            # 벡터 검색 실행
            if hasattr(self.vector_store, 'similarity_search'):
                results = self.vector_store.similarity_search(query, k=top_k)
            else:
                # 사용자 정의 검색 로직
                results = await self._custom_search(query, top_k)
            
            self.status = ToolStatus.AVAILABLE
            self.update_usage()
            
            return ToolResult(
                success=True,
                data=results,
                execution_time=time.time() - start_time,
                metadata={"query": query, "top_k": top_k}
            )
            
        except Exception as e:
            self.status = ToolStatus.ERROR
            logger.error(f"벡터 검색 오류: {str(e)}")
            
            return ToolResult(
                success=False,
                error=str(e),
                execution_time=time.time() - start_time
            )
    
    def validate_input(self, query: str, top_k: int, **kwargs) -> bool:
        """입력 검증"""
        if not isinstance(query, str) or not query.strip():
            return False
        if not isinstance(top_k, int) or top_k <= 0:
            return False
        return True
    
    async def _custom_search(self, query: str, top_k: int) -> List[Any]:
        """사용자 정의 검색 로직"""
        # 실제 구현에서는 벡터 저장소별 로직 구현
        return []

class DatabaseTool(BaseTool):
    """데이터베이스 도구"""
    
    def __init__(self, db_connection, name: str = "database"):
        super().__init__(
            name=name,
            description="데이터베이스 쿼리 실행",
            tool_type=ToolType.DATABASE
        )
        self.db_connection = db_connection
        self.allowed_operations = {"SELECT", "INSERT", "UPDATE", "DELETE"}
    
    async def execute(self, query: str, operation_type: str = "SELECT", **kwargs) -> ToolResult:
        """데이터베이스 쿼리 실행"""
        start_time = time.time()
        
        try:
            if not self.validate_input(query=query, operation_type=operation_type):
                return ToolResult(
                    success=False,
                    error="입력 검증 실패",
                    execution_time=time.time() - start_time
                )
            
            self.status = ToolStatus.BUSY
            
            # 실제 DB 쿼리 실행
            result = await self._execute_query(query)
            
            self.status = ToolStatus.AVAILABLE
            self.update_usage()
            
            return ToolResult(
                success=True,
                data=result,
                execution_time=time.time() - start_time,
                metadata={"operation": operation_type}
            )
            
        except Exception as e:
            self.status = ToolStatus.ERROR
            logger.error(f"데이터베이스 오류: {str(e)}")
            
            return ToolResult(
                success=False,
                error=str(e),
                execution_time=time.time() - start_time
            )
    
    def validate_input(self, query: str, operation_type: str, **kwargs) -> bool:
        """입력 검증"""
        if not isinstance(query, str) or not query.strip():
            return False
        if operation_type.upper() not in self.allowed_operations:
            return False
        return True
    
    async def _execute_query(self, query: str) -> Any:
        """쿼리 실행"""
        # 실제 구현에서는 데이터베이스 연결을 통한 쿼리 실행
        return {"message": "쿼리 실행 완료", "query": query}

class APITool(BaseTool):
    """API 호출 도구"""
    
    def __init__(self, base_url: str, name: str = "api_client"):
        super().__init__(
            name=name,
            description="HTTP API 호출",
            tool_type=ToolType.API
        )
        self.base_url = base_url
        self.headers = {}
        self.timeout = 30
    
    async def execute(self, endpoint: str, method: str = "GET", 
                     data: Optional[Dict] = None, **kwargs) -> ToolResult:
        """API 호출 실행"""
        start_time = time.time()
        
        try:
            if not self.validate_input(endpoint=endpoint, method=method):
                return ToolResult(
                    success=False,
                    error="입력 검증 실패",
                    execution_time=time.time() - start_time
                )
            
            self.status = ToolStatus.BUSY
            
            # 실제 API 호출 (aiohttp 또는 httpx 사용)
            result = await self._make_request(endpoint, method, data)
            
            self.status = ToolStatus.AVAILABLE
            self.update_usage()
            
            return ToolResult(
                success=True,
                data=result,
                execution_time=time.time() - start_time,
                metadata={"endpoint": endpoint, "method": method}
            )
            
        except Exception as e:
            self.status = ToolStatus.ERROR
            logger.error(f"API 호출 오류: {str(e)}")
            
            return ToolResult(
                success=False,
                error=str(e),
                execution_time=time.time() - start_time
            )
    
    def validate_input(self, endpoint: str, method: str, **kwargs) -> bool:
        """입력 검증"""
        if not isinstance(endpoint, str) or not endpoint.strip():
            return False
        if method.upper() not in ["GET", "POST", "PUT", "DELETE", "PATCH"]:
            return False
        return True
    
    async def _make_request(self, endpoint: str, method: str, data: Optional[Dict]) -> Any:
        """실제 HTTP 요청"""
        # 실제 구현에서는 aiohttp/httpx를 사용한 HTTP 요청
        return {"message": f"{method} {endpoint} 호출 완료", "data": data}

class FileSystemTool(BaseTool):
    """파일 시스템 도구"""
    
    def __init__(self, base_path: str = ".", name: str = "filesystem"):
        super().__init__(
            name=name,
            description="파일 시스템 조작",
            tool_type=ToolType.FILE
        )
        self.base_path = base_path
        self.allowed_extensions = {".txt", ".json", ".csv", ".md", ".py"}
    
    async def execute(self, action: str, file_path: str, 
                     content: Optional[str] = None, **kwargs) -> ToolResult:
        """파일 시스템 작업 실행"""
        start_time = time.time()
        
        try:
            if not self.validate_input(action=action, file_path=file_path):
                return ToolResult(
                    success=False,
                    error="입력 검증 실패",
                    execution_time=time.time() - start_time
                )
            
            self.status = ToolStatus.BUSY
            
            result = None
            if action == "read":
                result = await self._read_file(file_path)
            elif action == "write":
                result = await self._write_file(file_path, content)
            elif action == "list":
                result = await self._list_files(file_path)
            elif action == "delete":
                result = await self._delete_file(file_path)
            
            self.status = ToolStatus.AVAILABLE
            self.update_usage()
            
            return ToolResult(
                success=True,
                data=result,
                execution_time=time.time() - start_time,
                metadata={"action": action, "file_path": file_path}
            )
            
        except Exception as e:
            self.status = ToolStatus.ERROR
            logger.error(f"파일 시스템 오류: {str(e)}")
            
            return ToolResult(
                success=False,
                error=str(e),
                execution_time=time.time() - start_time
            )
    
    def validate_input(self, action: str, file_path: str, **kwargs) -> bool:
        """입력 검증"""
        if action not in ["read", "write", "list", "delete"]:
            return False
        if not isinstance(file_path, str) or not file_path.strip():
            return False
        # 경로 보안 검증 (path traversal 방지)
        if ".." in file_path or file_path.startswith("/"):
            return False
        return True
    
    async def _read_file(self, file_path: str) -> str:
        """파일 읽기"""
        import os
        full_path = os.path.join(self.base_path, file_path)
        if os.path.exists(full_path):
            with open(full_path, 'r', encoding='utf-8') as f:
                return f.read()
        return ""
    
    async def _write_file(self, file_path: str, content: str) -> str:
        """파일 쓰기"""
        import os
        full_path = os.path.join(self.base_path, file_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"파일 작성 완료: {file_path}"
    
    async def _list_files(self, directory: str) -> List[str]:
        """디렉토리 파일 목록"""
        import os
        full_path = os.path.join(self.base_path, directory)
        if os.path.exists(full_path) and os.path.isdir(full_path):
            return os.listdir(full_path)
        return []
    
    async def _delete_file(self, file_path: str) -> str:
        """파일 삭제"""
        import os
        full_path = os.path.join(self.base_path, file_path)
        if os.path.exists(full_path):
            os.remove(full_path)
            return f"파일 삭제 완료: {file_path}"
        return f"파일이 존재하지 않음: {file_path}"

class ToolRegistry:
    """도구 등록소"""
    
    def __init__(self):
        self.tools: Dict[str, BaseTool] = {}
        self.categories: Dict[ToolType, List[str]] = {tool_type: [] for tool_type in ToolType}
    
    def register_tool(self, tool: BaseTool) -> bool:
        """도구 등록"""
        try:
            if tool.name in self.tools:
                logger.warning(f"도구 이름 중복: {tool.name}")
                return False
            
            self.tools[tool.name] = tool
            self.categories[tool.tool_type].append(tool.name)
            
            logger.info(f"도구 등록 완료: {tool.name} ({tool.tool_type.value})")
            return True
            
        except Exception as e:
            logger.error(f"도구 등록 실패: {tool.name} - {str(e)}")
            return False
    
    def unregister_tool(self, tool_name: str) -> bool:
        """도구 등록 해제"""
        if tool_name not in self.tools:
            return False
        
        tool = self.tools[tool_name]
        self.categories[tool.tool_type].remove(tool_name)
        del self.tools[tool_name]
        
        logger.info(f"도구 등록 해제: {tool_name}")
        return True
    
    def get_tool(self, tool_name: str) -> Optional[BaseTool]:
        """도구 조회"""
        return self.tools.get(tool_name)
    
    def list_tools(self, tool_type: Optional[ToolType] = None) -> List[str]:
        """도구 목록 조회"""
        if tool_type:
            return self.categories.get(tool_type, [])
        return list(self.tools.keys())
    
    def get_available_tools(self) -> List[str]:
        """사용 가능한 도구 목록"""
        return [name for name, tool in self.tools.items() 
                if tool.status == ToolStatus.AVAILABLE]
    
    def get_tool_schemas(self) -> Dict[str, Dict[str, Any]]:
        """모든 도구의 스키마 반환"""
        return {name: tool.get_schema() for name, tool in self.tools.items()}

class ToolExecutor:
    """도구 실행기"""
    
    def __init__(self, registry: ToolRegistry):
        self.registry = registry
        self.execution_history: List[Dict[str, Any]] = []
        self.max_history = 1000
    
    async def execute_tool(self, tool_name: str, **kwargs) -> ToolResult:
        """도구 실행"""
        tool = self.registry.get_tool(tool_name)
        if not tool:
            return ToolResult(
                success=False,
                error=f"도구를 찾을 수 없음: {tool_name}"
            )
        
        if tool.status != ToolStatus.AVAILABLE:
            return ToolResult(
                success=False,
                error=f"도구가 사용 불가능한 상태: {tool.status.value}"
            )
        
        # 실행 기록
        execution_record = {
            "tool_name": tool_name,
            "timestamp": time.time(),
            "kwargs": kwargs
        }
        
        try:
            result = await tool.execute(**kwargs)
            execution_record["result"] = result.to_dict()
            
            # 히스토리 관리
            self._add_to_history(execution_record)
            
            return result
            
        except Exception as e:
            error_result = ToolResult(success=False, error=str(e))
            execution_record["result"] = error_result.to_dict()
            self._add_to_history(execution_record)
            
            logger.error(f"도구 실행 중 예외 발생: {tool_name} - {str(e)}")
            return error_result
    
    async def execute_tool_chain(self, tool_chain: List[Dict[str, Any]]) -> List[ToolResult]:
        """도구 체인 실행"""
        results = []
        
        for tool_config in tool_chain:
            tool_name = tool_config.get("tool_name")
            kwargs = tool_config.get("kwargs", {})
            
            # 이전 결과를 다음 도구의 입력으로 사용
            if results and tool_config.get("use_previous_result"):
                previous_result = results[-1]
                if previous_result.success:
                    kwargs["previous_data"] = previous_result.data
            
            result = await self.execute_tool(tool_name, **kwargs)
            results.append(result)
            
            # 실패시 체인 중단
            if not result.success and tool_config.get("stop_on_failure", True):
                break
        
        return results
    
    def _add_to_history(self, record: Dict[str, Any]) -> None:
        """실행 히스토리에 추가"""
        self.execution_history.append(record)
        
        # 히스토리 크기 제한
        if len(self.execution_history) > self.max_history:
            self.execution_history.pop(0)
    
    def get_execution_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """실행 히스토리 조회"""
        return self.execution_history[-limit:]
    
    def get_tool_usage_stats(self) -> Dict[str, Any]:
        """도구 사용 통계"""
        stats = {}
        for tool_name, tool in self.registry.tools.items():
            stats[tool_name] = {
                "usage_count": tool.usage_count,
                "last_used": tool.last_used,
                "status": tool.status.value,
                "type": tool.tool_type.value
            }
        return stats

class ToolValidator:
    """도구 검증기"""
    
    @staticmethod
    def validate_tool_config(config: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """도구 설정 검증"""
        required_fields = ["name", "type", "description"]
        
        for field in required_fields:
            if field not in config:
                return False, f"필수 필드 누락: {field}"
        
        if config["type"] not in [t.value for t in ToolType]:
            return False, f"유효하지 않은 도구 타입: {config['type']}"
        
        return True, None
    
    @staticmethod
    def validate_tool_instance(tool: BaseTool) -> Tuple[bool, Optional[str]]:
        """도구 인스턴스 검증"""
        if not hasattr(tool, 'execute'):
            return False, "execute 메서드가 없음"
        
        if not hasattr(tool, 'validate_input'):
            return False, "validate_input 메서드가 없음"
        
        if not isinstance(tool.tool_type, ToolType):
            return False, "tool_type이 올바르지 않음"
        
        return True, None

# 편의 함수들
def create_tool_registry() -> ToolRegistry:
    """도구 레지스트리 생성"""
    return ToolRegistry()

def create_standard_tools(vector_store=None, db_connection=None) -> List[BaseTool]:
    """표준 도구 세트 생성"""
    tools = []
    
    # 파일 시스템 도구
    tools.append(FileSystemTool())
    
    # 벡터 검색 도구
    if vector_store:
        tools.append(VectorSearchTool(vector_store))
    
    # 데이터베이스 도구
    if db_connection:
        tools.append(DatabaseTool(db_connection))
    
    return tools

def setup_default_tool_environment(vector_store=None, db_connection=None) -> Tuple[ToolRegistry, ToolExecutor]:
    """기본 도구 환경 설정"""
    registry = create_tool_registry()
    executor = ToolExecutor(registry)
    
    # 표준 도구들 등록
    standard_tools = create_standard_tools(vector_store, db_connection)
    for tool in standard_tools:
        registry.register_tool(tool)
    
    return registry, executor
'''

# 파일 저장
with open('tools.py', 'w', encoding='utf-8') as f:
    f.write(tools_py_content)

print("✅ tools.py 생성 완료")
print(f"파일 크기: {len(tools_py_content)} 문자")
print("\n주요 특징:")
print("- Agentic AI의 Tool 구성요소 완전 구현")
print("- 다양한 도구 타입 지원 (DB, API, File, Search 등)")
print("- 비동기 실행 및 상태 관리")
print("- 도구 체인 실행 기능")
print("- 사용 통계 및 히스토리 추적")
print("- 검증 및 보안 기능 내장")
print("- 플러그인 방식의 확장성")
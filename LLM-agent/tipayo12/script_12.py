# 사용 예제 코드 생성
usage_example_content = '''# usage_example.py - LangGraph RAG 시스템 사용 예제
# RPG 기반 경량화된 Agentic AI 시스템 데모

import asyncio
import os
from typing import Dict, Any

# 환경 변수 설정 예제
os.environ.setdefault("OPENAI_API_KEY", "your-openai-api-key")
os.environ.setdefault("PINECONE_API_KEY", "your-pinecone-api-key")  # 선택사항

from graph import GraphOrchestrator, GraphMode, run_rag_system
from db import create_database_manager_with_defaults
from utils import get_config, set_config

async def basic_usage_example():
    """기본 사용 예제"""
    print("=== 기본 RAG 시스템 사용 예제 ===")
    
    try:
        # 1. 간단한 질답
        result = await run_rag_system("안녕하세요, 반갑습니다!", mode="standard")
        print(f"답변: {result.get('answer', '')}")
        print(f"답변 타입: {result.get('answer_type', '')}")
        
        # 2. HR 관련 질문
        result = await run_rag_system("연차는 어떻게 사용하나요?", mode="standard")
        print(f"\\nHR 질문 답변: {result.get('answer', '')}")
        
        # 3. 복잡한 분석 작업
        result = await run_rag_system("우리 회사의 인사 정책을 종합적으로 분석해주세요", mode="rpg")
        print(f"\\nRPG 모드 답변: {result.get('answer', '')}")
        
    except Exception as e:
        print(f"기본 사용 예제 오류: {str(e)}")

async def advanced_usage_example():
    """고급 사용 예제 - 수동 구성"""
    print("\\n=== 고급 사용 예제 - 수동 구성 ===")
    
    try:
        # 1. 오케스트레이터 생성 및 초기화
        orchestrator = GraphOrchestrator()
        
        if not orchestrator.initialize_components():
            print("구성요소 초기화 실패")
            return
        
        # 2. 데이터베이스 설정
        if orchestrator.database_manager:
            # FAISS 로컬 DB 사용 (Pinecone이 없는 경우)
            success = await orchestrator.database_manager.connect_database("faiss")
            if success:
                print("FAISS 데이터베이스 연결 성공")
            else:
                # 메모리 DB 폴백
                success = await orchestrator.database_manager.connect_database("memory")
                print(f"메모리 데이터베이스 연결: {success}")
        
        # 3. 다양한 모드로 그래프 빌드 및 실행
        modes_to_test = [
            ("standard", "표준 RAG 모드"),
            ("rpg", "RPG 강화 모드"),
            ("autonomous", "자율 에이전트 모드"),
            ("coordinator", "조정 에이전트 모드")
        ]
        
        for mode_key, mode_name in modes_to_test:
            print(f"\\n--- {mode_name} 테스트 ---")
            
            try:
                # 그래프 빌드
                mode_enum = {
                    "standard": GraphMode.STANDARD,
                    "rpg": GraphMode.RPG_ENHANCED,
                    "autonomous": GraphMode.AUTONOMOUS,
                    "coordinator": GraphMode.COORDINATOR
                }[mode_key]
                
                orchestrator.build_graph(mode_enum)
                
                # 실행
                result = await orchestrator.run("LangGraph와 RPG를 활용한 시스템에 대해 설명해주세요")
                
                print(f"성공: {result.get('success', False)}")
                print(f"답변: {result.get('answer', '')[:100]}...")
                
            except Exception as e:
                print(f"{mode_name} 오류: {str(e)}")
        
    except Exception as e:
        print(f"고급 사용 예제 오류: {str(e)}")

async def document_loading_example():
    """문서 로딩 및 검색 예제"""
    print("\\n=== 문서 로딩 및 검색 예제 ===")
    
    try:
        # 데이터베이스 매니저 생성
        db_manager = create_database_manager_with_defaults()
        
        # 로컬 메모리 DB 연결 (데모용)
        success = await db_manager.connect_database("memory")
        if not success:
            print("데이터베이스 연결 실패")
            return
        
        # 샘플 문서 데이터 생성
        from langchain_core.documents import Document
        sample_docs = [
            Document(
                page_content="LangGraph는 상태 기반 멀티 에이전트 워크플로우를 구축하는 라이브러리입니다.",
                metadata={"source": "langgraph_guide.md", "topic": "langgraph"}
            ),
            Document(
                page_content="Repository Planning Graph(RPG)는 코드 생성을 위한 계획 그래프 방법론입니다.",
                metadata={"source": "rpg_paper.md", "topic": "rpg"}
            ),
            Document(
                page_content="Agentic AI는 자율적이고 목표 지향적인 AI 시스템을 의미합니다.",
                metadata={"source": "agentic_ai.md", "topic": "agentic_ai"}
            )
        ]
        
        # 문서 추가
        success = await db_manager.add_documents_to_active_db(sample_docs)
        if success:
            print(f"샘플 문서 {len(sample_docs)}개 추가 완료")
        
        # 검색 테스트
        queries = [
            "LangGraph란 무엇인가요?",
            "RPG에 대해 설명해주세요",
            "Agentic AI의 특징은?"
        ]
        
        for query in queries:
            print(f"\\n검색어: {query}")
            results = await db_manager.search_in_active_db(query, top_k=2)
            
            for i, doc in enumerate(results):
                print(f"  결과 {i+1}: {doc.page_content[:50]}...")
                print(f"  출처: {doc.metadata.get('source', 'unknown')}")
        
        # 데이터베이스 통계
        stats = await db_manager.get_database_stats()
        print(f"\\n데이터베이스 통계: {stats}")
        
    except Exception as e:
        print(f"문서 로딩 예제 오류: {str(e)}")

async def configuration_example():
    """설정 관리 예제"""
    print("\\n=== 설정 관리 예제 ===")
    
    try:
        from utils import get_config, set_config, save_config
        
        # 기본 설정 조회
        llm_config = get_config("llm")
        print(f"LLM 설정: {llm_config}")
        
        vector_db_config = get_config("vector_db")
        print(f"Vector DB 설정: {vector_db_config}")
        
        # 설정 변경
        set_config("llm.temperature", 0.2)
        set_config("vector_db.chunk_size", 800)
        
        # 도메인별 설정 조회
        hr_config = get_config("domains.hr", {})
        print(f"HR 도메인 설정: {hr_config}")
        
        # 설정 저장 (실제로는 파일에 저장됨)
        # save_success = save_config()
        # print(f"설정 저장 성공: {save_success}")
        
        print("설정 관리 예제 완료")
        
    except Exception as e:
        print(f"설정 관리 예제 오류: {str(e)}")

async def monitoring_example():
    """모니터링 및 성능 분석 예제"""
    print("\\n=== 모니터링 예제 ===")
    
    try:
        from utils import record_execution, get_metrics, profile
        
        # 성능 프로파일링 사용
        with profile("test_operation"):
            await asyncio.sleep(0.1)  # 가상의 작업
            print("프로파일링된 작업 완료")
        
        # 수동 실행 기록
        record_execution("test_component", "test_operation", 0.15, True, 
                        test_param="example_value")
        
        # 메트릭 조회
        metrics = get_metrics()
        print(f"\\n현재 메트릭:")
        print(f"  총 실행 수: {metrics.get('total_executions', 0)}")
        print(f"  업타임: {metrics.get('uptime', 0):.2f}초")
        
        component_metrics = metrics.get('component_metrics', {})
        for component, metric in component_metrics.items():
            print(f"  {component}: 평균 {metric.get('avg_duration', 0):.3f}초, "
                  f"성공률 {metric.get('success_rate', 0):.1%}")
        
    except Exception as e:
        print(f"모니터링 예제 오류: {str(e)}")

async def main():
    """메인 실행 함수"""
    print("🚀 LangGraph RPG RAG 시스템 사용 예제")
    print("=" * 50)
    
    try:
        # 각 예제 실행
        await basic_usage_example()
        await advanced_usage_example()
        await document_loading_example()
        await configuration_example()
        await monitoring_example()
        
        print("\\n✅ 모든 예제 실행 완료!")
        print("\\n📝 참고사항:")
        print("- 실제 사용시 OPENAI_API_KEY 환경변수를 설정하세요")
        print("- Pinecone 사용시 PINECONE_API_KEY도 설정하세요")
        print("- 문서 파일들을 data/ 폴더에 준비하세요")
        print("- 자세한 설정은 config.yaml 파일을 참조하세요")
        
    except Exception as e:
        print(f"\\n❌ 메인 실행 오류: {str(e)}")

if __name__ == "__main__":
    # 비동기 메인 함수 실행
    asyncio.run(main())
'''

# 설정 파일 예제 생성
config_yaml_content = '''# config.yaml - LangGraph RAG 시스템 설정 파일

# 시스템 전반 설정
system:
  log_level: INFO
  max_memory_usage: 1GB
  max_execution_time: 300

# LLM 설정
llm:
  default_model: gpt-4o-mini
  temperature: 0.1
  max_tokens: 1000
  timeout: 30

# 벡터 데이터베이스 설정
vector_db:
  default_type: faiss  # pinecone, faiss, memory 중 선택
  embedding_model: text-embedding-3-small
  chunk_size: 1000
  chunk_overlap: 200
  
  # Pinecone 설정 (사용시)
  pinecone:
    environment: us-east-1
    index_name: langgraph-rag
    dimension: 1536
  
  # FAISS 설정
  faiss:
    local_path: ./faiss_index
    save_interval: 300  # 5분마다 저장

# RPG (Repository Planning Graph) 설정
rpg:
  max_nodes: 50
  max_execution_time: 600
  enable_parallel_execution: true
  template_path: ./templates/rpg

# 메모리 시스템 설정
memory:
  short_term_size: 100
  short_term_ttl: 3600  # 1시간
  long_term_cache_size: 1000
  cleanup_interval: 300  # 5분

# 도메인별 설정
domains:
  hr:
    index_name: hr-rules
    documents_path: ./data/hr
    specialized_agents:
      - hr_policy_expert
      - hr_procedure_guide
    
  general:
    index_name: general-docs
    documents_path: ./data/general
    
  academic:
    index_name: academic-papers
    documents_path: ./data/papers

# 에이전트 설정
agents:
  llm_agents:
    gen:
      model: gpt-4o-mini
      temperature: 0.1
      max_tokens: 1500
    router1:
      model: gpt-4o-mini
      temperature: 0.0
      max_tokens: 500
    router2:
      model: gpt-4o-mini
      temperature: 0.0
      max_tokens: 500
  
  autonomous:
    max_iterations: 10
    planning_depth: 3
    enable_self_correction: true
  
  coordinator:
    max_concurrent_agents: 5
    timeout_per_agent: 60

# 라우팅 설정
routing:
  confidence_threshold: 0.7
  enable_llm_routing: true
  enable_rpg_routing: true
  fallback_route: rag_answer

# 도구 설정
tools:
  enable_file_tools: true
  enable_web_tools: false  # 보안상 기본 비활성화
  enable_database_tools: true
  tool_timeout: 30

# 모니터링 설정
monitoring:
  enable_metrics: true
  enable_profiling: true
  history_limit: 1000
  log_file: langgraph_rag.log

# 보안 설정
security:
  enable_input_validation: true
  max_input_length: 10000
  allowed_file_extensions:
    - .txt
    - .md
    - .pdf
    - .docx
  blocked_patterns:
    - "<script"
    - "javascript:"
    - "eval("
'''

# README 파일 생성
readme_content = '''# LangGraph RAG with RPG - 경량화된 Agentic AI 시스템

Repository Planning Graph(RPG) 논문의 핵심 로직을 경량화하여 LangGraph RAG에 통합한 차세대 AI 에이전트 시스템입니다.

## 🚀 주요 특징

### ✨ RPG(Repository Planning Graph) 통합
- 논문의 RPG 로직을 경량화하여 구현
- 3단계 실행: Planning → Refinement → Execution
- HTIL(Human-in-the-Loop)을 효율적으로 대체하는 자율 실행 시스템

### 🧠 Agentic AI 완전 구현
- **LLM**: 다양한 역할별 언어 모델 에이전트
- **Autonomy**: 목표 지향적 자율 계획 및 실행
- **Memory**: 단기/장기 메모리 분리 관리
- **Tool**: 플러그인 방식의 도구 시스템

### 🏗️ 모듈식 아키텍처
- 9개 독립 모듈로 구성된 Composable 설계
- 벤더 종속성 없는 추상화 계층
- 도메인별 동적 적응 시스템

### 🎯 최신 프롬프트 엔지니어링
- 2024-2025 최신 기법 적용
- 컨텍스트 기반 프롬프트 템플릿 엔진
- 역할별 특화 프롬프트 최적화

## 📁 모듈 구조

```
├── state.py          # 통합 상태 관리 시스템
├── rpg.py             # Repository Planning Graph 구현
├── memory.py          # Agentic AI Memory 시스템
├── tools.py           # Tool 인터페이스 관리
├── agents.py          # Agentic 구성 요소 (LLM, Autonomy)
├── db.py              # 벤더 독립적 데이터베이스 추상화
├── router.py          # 지능형 라우팅 시스템
├── utils.py           # 공통 유틸리티 (프롬프트, 설정, 모니터링)
├── graph.py           # 통합 그래프 오케스트레이션
└── requirements.txt   # 의존성 관리
```

## 🛠️ 설치 및 설정

### 1. 환경 설정
```bash
# 가상환경 생성 (권장)
python -m venv venv
source venv/bin/activate  # Windows: venv\\Scripts\\activate

# 의존성 설치
pip install -r requirements.txt
```

### 2. 환경변수 설정
```bash
# .env 파일 생성
OPENAI_API_KEY=your_openai_api_key
PINECONE_API_KEY=your_pinecone_api_key  # 선택사항
```

### 3. 설정 파일
`config.yaml` 파일에서 시스템 설정을 조정할 수 있습니다.

## 🎮 사용법

### 간단한 사용
```python
import asyncio
from graph import run_rag_system

async def main():
    # 기본 RAG 모드
    result = await run_rag_system("연차는 어떻게 사용하나요?", mode="standard")
    print(result['answer'])
    
    # RPG 강화 모드  
    result = await run_rag_system("복잡한 업무 프로세스를 분석해주세요", mode="rpg")
    print(result['answer'])
    
    # 자율 에이전트 모드
    result = await run_rag_system("자동으로 최적화해주세요", mode="autonomous")
    print(result['answer'])

asyncio.run(main())
```

### 고급 사용 (수동 구성)
```python
from graph import GraphOrchestrator, GraphMode

# 오케스트레이터 생성
orchestrator = GraphOrchestrator()
orchestrator.initialize_components()

# 데이터베이스 연결
await orchestrator.database_manager.connect_database("faiss")

# 그래프 빌드 및 실행
orchestrator.build_graph(GraphMode.RPG_ENHANCED)
result = await orchestrator.run("사용자 질문")
```

## 🔧 주요 기능

### 1. RPG 기반 지능형 계획
- 사용자 요청을 능력 그래프로 분해
- 의존성 기반 실행 순서 자동 결정
- 실패 시 자동 복구 및 재시도

### 2. 다중 에이전트 협업
- LLM 에이전트: 텍스트 처리 및 생성 전담
- 자율 에이전트: 목표 지향적 계획 및 실행
- 조정 에이전트: 다중 에이전트 오케스트레이션

### 3. 지능형 라우팅
- 규칙 기반 + LLM 기반 + RPG 기반 통합 라우팅
- 실시간 성능 모니터링 및 최적화
- 컨텍스트 기반 동적 경로 선택

### 4. 메모리 시스템
- 단기 메모리: LRU 기반 세션 컨텍스트 관리
- 장기 메모리: 벡터 저장소 연동 지식 관리
- 자동 메모리 정리 및 이주 기능

### 5. 도구 생태계
- 벡터 검색, 데이터베이스, API, 파일 시스템 도구
- 비동기 실행 및 체인 처리
- 사용 통계 및 성능 분석

## 🌟 RPG 핵심 개념

### 논문의 RPG 로직 구현
1. **Proposal-level Planning**: 사용자 요청을 기능 노드로 분해
2. **Implementation-level Refinement**: 기능을 실행 가능한 단위로 정제  
3. **Graph-guided Execution**: 의존성 그래프 기반 순차 실행

### HTIL 대체 메커니즘
- 사람의 개입 없이 자율적 의사결정
- 실패 시 자동 복구 및 개선
- 컨텍스트 기반 동적 계획 수정

## 🔄 아키텍처 원칙

### Composability (조합성)
- 각 모듈은 독립적으로 교체 가능
- 인터페이스 기반 느슨한 결합
- 런타임 의존성 주입

### Vendor Independence (벤더 독립성)  
- Pinecone, FAISS, 로컬 메모리 DB 지원
- OpenAI 외 다른 LLM 제공자 지원 가능
- 클라우드 및 온프레미스 배포 지원

### Domain Agnostic (도메인 무관성)
- 설정 기반 도메인 템플릿
- 동적 프롬프트 생성
- 업무별 특화 에이전트 구성

## 📊 성능 및 모니터링

### 내장 모니터링
- 실행 시간 및 성공률 추적
- 컴포넌트별 성능 메트릭
- 메모리 사용량 모니터링

### 프로파일링
```python
from utils import profile

with profile("custom_operation"):
    # 측정하고 싶은 코드
    pass
```

### 설정 기반 튜닝
- YAML 기반 실시간 설정 변경
- A/B 테스트 지원
- 성능 임계값 알람

## 🤝 기여 가이드

### 새로운 에이전트 추가
```python
from agents import BaseAgent, AgentType

class CustomAgent(BaseAgent):
    def __init__(self, name: str):
        super().__init__(name, AgentType.CUSTOM)
    
    async def execute(self, task: str, context: Dict, state: ComposableState):
        # 에이전트 로직 구현
        pass
```

### 새로운 도구 추가
```python
from tools import BaseTool, ToolType

class CustomTool(BaseTool):
    def __init__(self):
        super().__init__("custom_tool", "설명", ToolType.CUSTOM)
    
    async def execute(self, **kwargs):
        # 도구 로직 구현
        pass
```

## 📈 로드맵

### v1.1 (예정)
- [ ] 다국어 지원
- [ ] 웹 UI 대시보드
- [ ] 고급 RAG 기법 (HyDE, CoVe)

### v1.2 (예정)  
- [ ] 분산 처리 지원
- [ ] 커스텀 LLM 제공자 추가
- [ ] 고급 메모리 압축

## 🐛 이슈 및 지원

버그 리포트나 기능 요청은 Issues에 등록해 주세요.

## 📄 라이센스

MIT License - 자유롭게 사용, 수정, 배포 가능합니다.

---

**Built with ❤️ by the LangGraph RPG Team**

*"논문의 혁신을 실제 코드로 구현하여, 누구나 사용할 수 있는 경량화된 Agentic AI 시스템을 제공합니다."*
'''

# 파일들 저장
with open('usage_example.py', 'w', encoding='utf-8') as f:
    f.write(usage_example_content)

with open('config.yaml', 'w', encoding='utf-8') as f:
    f.write(config_yaml_content)

with open('README.md', 'w', encoding='utf-8') as f:
    f.write(readme_content)

print("✅ 추가 파일들 생성 완료!")
print(f"usage_example.py 크기: {len(usage_example_content)} 문자")
print(f"config.yaml 크기: {len(config_yaml_content)} 문자")
print(f"README.md 크기: {len(readme_content)} 문자")

print("\n🎉 LangGraph RPG RAG 시스템 리팩터링 완료!")
print("=" * 60)
print("📁 생성된 파일 목록:")
file_list = [
    "state.py", "rpg.py", "memory.py", "tools.py", "agents.py",
    "db.py", "router.py", "utils.py", "graph.py", "requirements.txt",
    "usage_example.py", "config.yaml", "README.md"
]

for i, file_name in enumerate(file_list, 1):
    print(f"{i:2d}. {file_name}")

print(f"\n📊 총 {len(file_list)}개 파일 생성")
print("\n🚀 다음 단계:")
print("1. 환경변수 설정 (.env 파일)")
print("2. pip install -r requirements.txt")
print("3. python usage_example.py")
print("4. 문서 데이터를 ./data/ 폴더에 준비")
print("5. config.yaml에서 설정 조정")

print("\n✨ 주요 혁신 사항:")
print("- 📈 RPG 논문 로직의 실용적 경량화")
print("- 🤖 완전한 Agentic AI 구성 요소 구현")  
print("- 🔧 HTIL 대체 자율 시스템")
print("- 🌐 벤더 독립적 아키텍처")
print("- 📝 최신 프롬프트 엔지니어링")
print("- 🔀 Composable 모듈 설계")
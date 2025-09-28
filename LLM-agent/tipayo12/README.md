# LangGraph RAG with RPG - 경량화된 Agentic AI 시스템

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
source venv/bin/activate  # Windows: venv\Scripts\activate

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

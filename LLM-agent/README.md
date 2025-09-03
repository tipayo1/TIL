# LangChain Auto-GPT 에이전트

LangChain 프레임워크를 사용하여 구현한 Auto-GPT 스타일의 자율 AI 에이전트입니다.

## 🚀 주요 특징

- **자율적 계획 수립**: 목표를 받아 자동으로 단계별 계획을 세우고 실행
- **다양한 도구 활용**: 웹 검색, 파일 관리, 계산, 시간 확인 등
- **벡터 메모리**: FAISS 기반 장기 메모리 시스템
- **ReAct 패턴**: Reasoning + Acting 방식으로 사고하며 행동
- **모니터링**: 작업 수행 과정 추적 및 성능 분석

## 📋 필수 요구사항

- Python 3.8 이상
- OpenAI API 키
- SerpAPI 키 (선택사항, 웹 검색용)

## 🛠 설치 방법

1. **저장소 클론 및 이동**
   ```bash
   # 파일들을 다운로드한 폴더로 이동
   cd your_project_folder
   ```

2. **가상환경 생성 및 활성화** (권장)
   ```bash
   python -m venv autogpt_env

   # Windows
   autogpt_env\Scripts\activate

   # Mac/Linux
   source autogpt_env/bin/activate
   ```

3. **필수 패키지 설치**
   ```bash
   pip install -r requirements.txt
   ```

## 🔑 API 키 설정

### 방법 1: 환경변수 파일 (.env)
프로젝트 폴더에 `.env` 파일을 생성하고 다음 내용을 입력:

```env
OPENAI_API_KEY=your_openai_api_key_here
SERPAPI_API_KEY=your_serpapi_key_here
```

### 방법 2: 직접 입력
스크립트 실행 시 API 키를 직접 입력할 수 있습니다.

## 📖 사용 방법

### 1. Jupyter Notebook 버전 (권장)

```bash
jupyter notebook langchain_autogpt_agent.ipynb
```

Jupyter Notebook에서 셀을 순서대로 실행하면서 단계별로 학습하고 테스트할 수 있습니다.

### 2. Python 스크립트 버전

```bash
python simple_autogpt_agent.py
```

명령줄에서 바로 실행할 수 있는 간단한 버전입니다.

## 📝 사용 예제

### 예제 1: 연구 및 보고서 작성
```python
goals = [
    "Python의 주요 특징에 대해 조사하고 정리하기",
    "조사한 내용을 'python_features.txt' 파일로 저장하기",
    "파일이 제대로 저장되었는지 확인하기"
]

result = autogpt_agent.run(goals)
```

### 예제 2: 계산 및 분석
```python
goals = [
    "현재 시간을 확인하기",
    "1부터 100까지의 합을 계산하기",
    "계산 결과와 현재 시간을 포함한 보고서를 'calculation_report.txt' 파일로 작성하기"
]

result = autogpt_agent.run(goals)
```

### 예제 3: 웹 검색 및 요약
```python
goals = [
    "인공지능의 최신 동향에 대해 웹에서 검색하기",
    "검색한 정보를 요약하고 분석하기",
    "분석 결과를 'ai_trends_analysis.txt' 파일로 저장하기"
]

result = autogpt_agent.run(goals)
```

## 🛠 사용 가능한 도구들

1. **search**: 웹 검색 (SerpAPI 필요)
2. **write_file**: 파일 작성
3. **read_file**: 파일 읽기
4. **calculator**: 수학 계산
5. **current_time**: 현재 시간 확인

## 🧠 메모리 시스템

- **벡터 데이터베이스**: FAISS 사용
- **임베딩 모델**: OpenAI text-embedding-3-small
- **검색**: 유사도 기반 관련 정보 검색
- **저장**: 작업 과정과 결과를 자동 저장

## ⚙️ 설정 옵션

### LLM 모델 변경
```python
llm = ChatOpenAI(
    model_name="gpt-4",  # 또는 "gpt-3.5-turbo"
    temperature=0.1,     # 창의성 조절 (0.0-1.0)
    max_tokens=2000      # 최대 출력 토큰 수
)
```

### 최대 반복 횟수 조절
```python
result = autogpt_agent.run(goals, max_iterations=20)
```

## 🔍 모니터링 및 디버깅

시스템에는 성능 모니터링 기능이 포함되어 있습니다:

```python
# 성능 보고서 확인
show_performance_report()

# 시스템 정보 확인
show_system_info()

# 메모리 상태 확인
manage_memory()
```

## 🚨 주의사항

1. **API 요금**: OpenAI API 사용에 따른 요금이 부과됩니다.
2. **파일 권한**: 파일 읽기/쓰기 권한을 확인하세요.
3. **네트워크**: 웹 검색 기능을 위해 인터넷 연결이 필요합니다.
4. **반복 제한**: 무한 루프 방지를 위해 최대 반복 횟수를 설정하세요.

## 🐛 문제 해결

### 1. 패키지 설치 오류
```bash
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

### 2. API 키 오류
- API 키가 올바른지 확인
- API 키에 충분한 크레딧이 있는지 확인
- 환경변수 설정을 다시 확인

### 3. 메모리 오류
```bash
# CPU 버전으로 FAISS 재설치
pip uninstall faiss-cpu faiss-gpu -y
pip install faiss-cpu
```

## 🔧 고급 사용법

### 1. 커스텀 도구 추가
```python
def my_custom_tool(input_text: str) -> str:
    # 사용자 정의 로직
    return f"처리된 결과: {input_text}"

custom_tool = Tool(
    name="custom_tool",
    func=my_custom_tool,
    description="사용자 정의 도구 설명"
)

tools.append(custom_tool)
```

### 2. 메모리에 정보 추가
```python
autogpt_agent.add_memory("중요한 정보를 메모리에 저장")
```

### 3. 작업 모니터링
```python
result = run_monitored_task(goals, "작업명")
```

## 📚 추가 학습 자료

- [LangChain 공식 문서](https://python.langchain.com/)
- [OpenAI API 가이드](https://platform.openai.com/docs/)
- [FAISS 문서](https://faiss.ai/)
- [Auto-GPT 원본 프로젝트](https://github.com/Significant-Gravitas/Auto-GPT)

## 🤝 기여하기

이 프로젝트는 학습 목적으로 만들어졌습니다. 개선 사항이나 버그를 발견하시면 이슈를 남겨주세요.

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 🆘 지원

문제가 발생하거나 질문이 있으시면:
1. 이 README의 문제 해결 섹션을 확인하세요
2. 공식 LangChain 문서를 참고하세요
3. OpenAI API 상태를 확인하세요

---

**⚠️ 면책 조항**: 이 도구는 교육 및 실험 목적으로 만들어졌습니다. 프로덕션 환경에서 사용하기 전에 충분한 테스트를 진행하세요.

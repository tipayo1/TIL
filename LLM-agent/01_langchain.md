
---

# 🚀 LangChain 시작하기

LangChain은 **LLM을 외부 데이터 소스나 다른 컴포넌트와 연결**하여 강력한 애플리케이션을 만들 수 있도록 돕는 프레임워크입니다.  

---

## 🔑 주요 구성 요소

- **LLM/Chat Model** : 언어 모델 자체 (`ChatOpenAI` 같은 클래스 사용)  
- **Prompt Template** : LLM에 전달할 지시문을 동적으로 생성하는 템플릿  
- **Output Parser** : 모델의 출력(e.g. `AIMessage`)을 원하는 형식(e.g. `string`)으로 변환  
- **Chain (LCEL)** : 구성 요소들을 `|` 연산자로 연결해 실행 흐름(Chain) 구성  

---

## 1. 기본 사용법

### ✅ 환경 설정 및 모델 초기화
```
# 필요한 라이브러리 설치
# %pip install -q langchain langchain-openai python-dotenv

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

# .env 파일에서 API 키 로드
load_dotenv()

# LLM 모델 초기화
llm = ChatOpenAI(model='gpt-4.1-nano')
```

### ✅ 기본 호출 (invoke, stream, batch)
```
# 단일 호출
response = llm.invoke("Hello, world!")
print(response.content)

# 스트리밍 호출
for token in llm.stream("LangChain에 대해 설명해줘"):
    print(token.content, end="")

# 배치 호출
responses = llm.batch(["LangChain이란?", "LangSmith란?"])
print([res.content for res in responses])
```

---

## 2. 프롬프트(Prompt) 다루기

프롬프트 = **Instruction(지시) + Context(맥락) + Memory(기억)**  

---

### (1) PromptTemplate (단발성 명령)
```
from langchain_core.prompts import PromptTemplate

template = "{country}의 수도는 어디인가요?"
prompt = PromptTemplate.from_template(template)

# 체인 연결
chain = prompt | llm
response = chain.invoke({"country": "대한민국"})
print(response.content)
# >> 대한민국의 수도는 서울입니다.
```

---

### (2) ChatPromptTemplate (채팅 형식)
```
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

chat_template = ChatPromptTemplate.from_messages([
    ('system', '당신은 {lang}으로 번역하는 번역가입니다.'),
    ('human', '{text}를 번역해주세요.')
])

# 체인 구성
chain = chat_template | llm | StrOutputParser()

# 실행
result = chain.invoke({'lang': '영어', 'text': '버거가 먹고싶다'})
print(result)
# >> I want to eat a burger.
```

---

### (3) Few-Shot Prompting (소수 예시 학습)
```
from langchain_core.prompts import FewShotPromptTemplate, PromptTemplate

# 1. 예시 데이터 정의
examples = [
    {
        "question": "네이버의 창립자는 언제 태어났나요?",
        "answer": """이 질문에 추가 질문이 필요한가요: 예.
추가 질문: 네이버의 창립자는 누구인가요?
중간 답변: 네이버는 이해진에 의해 창립되었습니다.
추가 질문: 이해진은 언제 태어났나요?
중간 답변: 이해진은 1967년 6월 22일에 태어났습니다.
최종 답변은: 1967년 6월 22일
""",
    },
]

# 2. 예시 포맷팅
example_prompt = PromptTemplate.from_template(
    "Question:\n{question}\nAnswer:\n{answer}"
)

# 3. FewShotPromptTemplate 생성
prompt = FewShotPromptTemplate(
    examples=examples,
    example_prompt=example_prompt,
    suffix="Question:\n{question}\nAnswer:", # 실제 질문 들어갈 부분
    input_variables=["question"],
)

# 4. 체인 실행
chain = prompt | llm | StrOutputParser()
result = chain.invoke({"question": "Google이 창립된 연도에 Bill Gates의 나이는 몇 살인가요?"})
print(result)
```

**실행 결과 예시**
```
이 질문에 추가 질문이 필요한가요: 예.
추가 질문: Google은 언제 창립되었나요?
중간 답변: Google은 1998년에 창립되었습니다.
추가 질문: Bill Gates는 언제 태어났나요?
중간 답변: Bill Gates는 1955년 10월 28일에 태어났습니다.
추가 질문: 1998년에 Bill Gates의 나이는 몇 살이었나요?
중간 답변: 1998년 - 1955년 = 43년. Bill Gates는 43세였습니다.
최종 답변은: 43세
```

---

## 3. LangChain Hub

전 세계 개발자들이 공유하는 **유용한 프롬프트 저장소**  

```
from langchain import hub

# React 에이전트 프롬프트를 hub에서 가져오기
prompt = hub.pull('hwchase17/react')
# print(prompt.template) # 프롬프트 내용 확인
```

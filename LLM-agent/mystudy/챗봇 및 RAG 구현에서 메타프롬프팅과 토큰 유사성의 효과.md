<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" class="logo" width="120"/>

## 챗봇 및 RAG 구현에서 메타프롬프팅과 토큰 유사성의 효과

### 메타프롬프팅이란?

메타프롬프팅(Meta prompting)은 AI 챗봇에게 직접적인 질문을 하는 대신, 챗봇 또는 LLM에게 '더 좋은 프롬프트'를 생성하거나 기존 프롬프트를 개선·분석하도록 유도하는 고차원적 프롬프트 엔지니어링 기법입니다. 실제 챗봇 제작이나 Retrieval-Augmented Generation(RAG) 시스템에서, 메타프롬프팅은 구조적이고 목적 지향적인 프롬프트 최적화를 가능하게 합니다[^1_1][^1_2][^1_3].

### RAG와 메타프롬프팅의 성능 향상 예시

- **RAG 시스템에서의 메타프롬프팅**: 최근 연구에서 메타프롬프팅 최적화 기법을 적용해, 검색-생성(Retrieval-Augmented Generation, RAG) 시스템의 성능이 기존보다 30% 이상 향상됨을 확인했습니다. 즉, 검색으로 얻은 정보를 단순히 합치는 것보다, 메타프롬프트로 필터링·정제(예: 요약, 잡음 제거)해서 주입하면, LLM의 응답의 정확성과 일관성이 크게 증가합니다[^1_4][^1_5][^1_6][^1_7][^1_8].
- **실제 적용 방식**: 검색 결과(텍스트)들을 보정하는 프롬프트를 LLM이 스스로 생성·점검하며, 가장 효과적인 instruction을 반복적으로 찾는 메타프롬프팅 과정을 거칩니다. 이를 통해 더 적합한 지식이 LLM 입력에 반영되고, 출력의 품질(정확성, 일관성, 신뢰도 등)이 높아집니다[^1_8].


### 비슷한 토큰(유사 표현)과 LLM 성능의 상관관계

- **토큰 유사성의 일반적 영향**: LLM은 유사한 어휘·토큰이 포함된 프롬프트에서 더 일관되고 예측 가능한 출력을 내는 경우가 많습니다. 메타프롬프팅은 구조적이고 논리적인 프롬프트(즉, 비슷한 토큰 분포, 반복되는 명령어, 목적 중심의 체계 등)를 유도하므로, 모델이 내재한 언어 모델링 특성과 맞아떨어져 결과 품질이 높아집니다[^1_2][^1_3].
- **언어별/토크나이저 연구**: 특히 한국어처럼 복합적 토크나이저가 필요한 언어에서는, 적절한 토큰화 전략이 모델의 예측 안정성을 높이고, 정답에 더 가까운 출력을 유도할 수 있습니다. 유사한 토큰 분포를 가진 입력이 일관된 출력을 유도하는 사례가 실험적으로도 보고되고 있습니다[^1_9].
- **주의점**: 단순히 토큰이 비슷하다고 해서 무조건 좋은 결과가 나오지는 않습니다. '반복 토큰 현상'처럼 LLM이 동일 토큰 반복에 과도히 집착하는 경우 오히려 정확도가 손상될 수 있으니, 메타프롬프팅은 반복이 아닌, 의미상 유사성·구조적 논리를 강화하는 데에 중점을 둬야 합니다[^1_10].


### 결론

- 메타프롬프팅은 챗봇 및 RAG에서 **더 좋은, 목적 적합적 프롬프트**를 자동 생성·개선해 LLM의 성능(정확성, 신뢰성, 일관성) 향상에 기여합니다.
- 메타프롬프팅은 비슷한 토큰 분포와 구조적 일관성을 자연스럽게 유도하므로, 모델이 최적의 결과를 내기 쉬운 환경을 만들 수 있습니다[^1_2][^1_4][^1_8].
- 단, 무분별한 반복이나 단순 토큰 유사성은 오히려 오작동을 유발할 수 있으므로, 메타프롬프팅의 설계에서 *의미 체계, 논리, 목적 중심*을 우선시해야 성능 향상이 일어납니다[^1_10].


#### 참고 키포인트

- **메타프롬프팅 최적화**로 RAG 응답 품질 30% 이상 향상[^1_4][^1_6][^1_7][^1_8].
- **비슷한 토큰 사용**은 프롬프트 구조화 및 목적 명확성에 도움, 단 무분별한 반복은 주의.
- **언어별 토큰화 전략**의 중요성: 구조적/유사 토큰이 LLM 품질을 좌우할 수 있음[^1_9].

<div style="text-align: center">⁂</div>

[^1_1]: https://aitoolsclub.com/what-is-meta-prompting-how-to-guide-generative-ai-chatbots-to-create-and-refine-prompts/

[^1_2]: https://www.geeksforgeeks.org/meta-prompting/

[^1_3]: https://www.godofprompt.ai/blog/guide-for-meta-prompting

[^1_4]: https://paperswithcode.com/paper/meta-prompting-optimized-retrieval-augmented

[^1_5]: https://www.aimodels.fyi/papers/arxiv/meta-prompting-optimized-retrieval-augmented-generation

[^1_6]: http://arxiv.org/pdf/2407.03955.pdf

[^1_7]: https://arxiv.org/html/2407.03955v1

[^1_8]: https://www.themoonlight.io/en/review/meta-prompting-optimized-retrieval-augmented-generation

[^1_9]: https://arxiv.org/html/2502.12560v2

[^1_10]: http://www.arxiv.org/pdf/2503.08908.pdf

[^1_11]: https://www.reddit.com/r/PromptEngineering/comments/1lmo4cw/curiosity_and_goaldriven_metaprompting_techniques/

[^1_12]: https://techcrunch.com/2025/07/15/meta-fixes-bug-that-could-leak-users-ai-prompts-and-generated-content/

[^1_13]: https://tilburg.ai/2024/12/meta-prompting/

[^1_14]: https://www.technology.org/2025/07/04/meta-introduces-ai-chatbots-that-initiate-contact-without-user-prompts/

[^1_15]: https://openreview.net/forum?id=5SZ1STXB93

[^1_16]: https://americanlightworkers.com/meta-prompting-the-future-of-ai-prompt-collaboration-d4e7c4070f25

[^1_17]: https://openreview.net/forum?id=6o9QUqUq9f

[^1_18]: https://www.cyberdaily.au/security/12388-meta-patches-ai-chatbot-bug-capable-of-leaking-user-ai-prompts-and-responses

[^1_19]: https://www.datasor.no/reducing-output-tokens-in-large-language-model-inference-through-smarter-prompting/

[^1_20]: https://www.tomsguide.com/computing/online-security/meta-ai-was-leaking-chatbot-prompts-and-answers-to-unauthorized-users


---

# 텔레그램 갓파더 챗봇: "로또" 자동 번호 생성기 구현 단계별 가이드

로또 번호 자동 생성 기능을 "로또"라는 명령어로 제공하는 텔레그램 갓파더 챗봇을 만들고자 할 때, 아래와 같이 각 과정별로 문제를 잘게 나눠 단계별로 진행할 수 있습니다.

## 1. 챗봇 기초 환경 준비

- **텔레그램 계정 생성 및 로그인**
- **BotFather(갓파더)에서 새 봇 생성**
    - /newbot 명령어 입력 후 이름/사용자이름 설정
    - 발급받은 API 토큰 별도 저장
- **개발 환경 구축**
    - Python, Node.js 등 챗봇 서버 구동 언어 선택
    - 기본 텔레그램 Bot API 라이브러리 설치 (예: python-telegram-bot)


## 2. 챗봇 서버 구현

- **API 토큰과 라이브러리로 챗봇 서버 연결**
- **메시지 수신 핸들러 구성**
    - 사용자의 모든 입력 메시지를 인식
- **"로또" 명령어 인식 코드 작성**
    - 메시지가 "로또"일 때만 반응하도록 필터 추가


## 3. 로또 번호 자동 생성기 구현

- **로또 번호 생성 로직 추가**
    - 1~45 숫자 중 중복 없이 6개를 임의로 추출 (파이썬 예시: `random.sample(range(1,46), 6)`)
    - 번호를 오름차순 정렬 후 문자열로 변환


## 4. 사용자 메시지 응답 구조

- **"로또" 입력 시 자동 생성된 번호를 사용자에게 전송**
- **실행 예시**
    - 유저: "로또"
    - 봇: "이번주 추천 로또 번호: 3, 11, 15, 22, 36, 44"


## 5. 코드 테스트 및 배포

- **직접 챗방에서 명령어를 입력하여 제대로 동작하는지 검증**
- **에러 및 예외 처리(예: 잘못된 명령 입력시 안내문)**
- **서버 클라우드, 홈 PC 등에서 챗봇 서비스 운영**


## 6. 추가 고도화(선택)

- 여러 조합 제공, 날짜별 기록, 당첨 확인 기능 등 부가기능 추가 고려


### 예시 Python 코드(핵심로직)

```python
import random
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

def lotto_handler(update, context):
    nums = sorted(random.sample(range(1, 46), 6))
    reply = f"이번주 추천 로또 번호: {', '.join(map(str, nums))}"
    update.message.reply_text(reply)

updater = Updater('YOUR_API_TOKEN', use_context=True)
dp = updater.dispatcher
dp.add_handler(MessageHandler(Filters.text & Filters.regex('로또'), lotto_handler))
updater.start_polling()
```

> 위 코드는 실제 챗봇 구현을 위한 참고용 핵심 부분만 발췌한 예시입니다.
> 기본적인 텔레그램 챗봇 개발자 문서 또는 라이브러리 예제를 참고하여 각 환경에 맞게 수정할 수 있습니다.

## 요약

1. 챗봇 생성 및 API 연동
2. "로또" 입력 감지 핸들러 구성
3. 로또번호 생성 코드 구현(1~45 중 6개 무작위)
4. 자동생성 번호 사용자 응답
5. 테스트 후 서비스 배포

이와 같은 세부 단계로 진행하면, 텔레그램 챗봇에서 "로또"라고 입력하면 자동으로 번호를 생성해주는 기능을 쉽고 체계적으로 구현할 수 있습니다.

---

# import random

def lotto():
    nums = sorted(random.sample(range(1, 46), 6))

print(lotto())

수정

현재 작성하신 코드를 보면, `lotto()` 함수가 번호 리스트를 생성하긴 하지만 그 결과를 반환하지 않아서, `print(lotto())` 호출 시 `None`이 출력됩니다. 함수가 생성한 번호 리스트를 반환하도록 수정해야 합니다.

아래처럼 수정해보세요:

```python
import random

def lotto():
    nums = sorted(random.sample(range(1, 46), 6))
    return nums  # 생성한 번호 리스트 반환

print(lotto())  # 예: [3, 11, 15, 22, 36, 44]
```

이렇게 하면 `lotto()` 함수가 번호 리스트를 반환하고, `print`로 출력할 수 있습니다.

추가로, 문자열 형태로 출력하고 싶다면 이렇게도 할 수 있습니다:

```python
def lotto():
    nums = sorted(random.sample(range(1, 46), 6))
    return ", ".join(map(str, nums))

print("이번주 추천 로또 번호:", lotto())
```

필요한 형태에 맞게 활용해 보세요!

---

# data = {

"ok": True,
    "result": [
        {
            "update_id": 274512681,
            "message": {
                "message_id": 3,
                "from": {
                    "id": 8469805461,
                    "is_bot": False,
                    "first_name": "pangyi",
                    "language_code": "ko"
                },
                "chat": {
                    "id": 8469805461,
                    "first_name": "pangyi",
                    "type": "private"
                },
                "date": 1753323133,
                "text": "/기능"
            }
        },
        {
            "update_id": 274512682,
            "message": {
                "message_id": 4,
                "from": {
                    "id": 8469805461,
                    "is_bot": False,
                    "first_name": "pangyi",
                    "language_code": "ko"
                },
                "chat": {
                    "id": 8469805461,
                    "first_name": "pangyi",
                    "type": "private"
                },
                "date": 1753323139,
                "text": "/option",
                "entities": [
                    {
                        "offset": 0,
                        "length": 7,
                        "type": "bot_command"
                    }
                ]
            }
        },
        {
            "update_id": 274512683,
            "message": {
                "message_id": 5,
                "from": {
                    "id": 8469805461,
                    "is_bot": False,
                    "first_name": "pangyi",
                    "language_code": "ko"
                },
                "chat": {
                    "id": 8469805461,
                    "first_name": "pangyi",
                    "type": "private"
                },
                "date": 1753323541,
                "text": "/help",
                "entities": [
                    {
                        "offset": 0,
                        "length": 5,
                        "type": "bot_command"
                    }
                ]
            }
        },
        {
            "update_id": 274512684,
            "message": {
                "message_id": 10,
                "from": {
                    "id": 8469805461,
                    "is_bot": False,
                    "first_name": "pangyi",
                    "language_code": "ko"
                },
                "chat": {
                    "id": 8469805461,
                    "first_name": "pangyi",
                    "type": "private"
                },
                "date": 1753330825,
                "text": "로또"
            }
        }
    ]
}

마지막 "text":를 바꿔서 로또뽑는걸로 바꿔줘

주어진 `data` 딕셔너리에서, 가장 마지막 `"text"` 필드를 `"로또뽑기"` 혹은 원하는 문구로 변경하려면 아래처럼 수정할 수 있습니다:

```python
data['result'][-1]['message']['text'] = "로또뽑기"
```

변경 후 `data`의 마지막 메시지는 `"text": "로또뽑기"`가 됩니다.

전체 예시:

```python
data = {
    "ok": True,
    "result": [
        {
            "update_id": 274512681,
            "message": {
                "message_id": 3,
                "from": {
                    "id": 8469805461,
                    "is_bot": False,
                    "first_name": "pangyi",
                    "language_code": "ko"
                },
                "chat": {
                    "id": 8469805461,
                    "first_name": "pangyi",
                    "type": "private"
                },
                "date": 1753323133,
                "text": "/기능"
            }
        },
        {
            "update_id": 274512682,
            "message": {
                "message_id": 4,
                "from": {
                    "id": 8469805461,
                    "is_bot": False,
                    "first_name": "pangyi",
                    "language_code": "ko"
                },
                "chat": {
                    "id": 8469805461,
                    "first_name": "pangyi",
                    "type": "private"
                },
                "date": 1753323139,
                "text": "/option",
                "entities": [
                    {
                        "offset": 0,
                        "length": 7,
                        "type": "bot_command"
                    }
                ]
            }
        },
        {
            "update_id": 274512683,
            "message": {
                "message_id": 5,
                "from": {
                    "id": 8469805461,
                    "is_bot": False,
                    "first_name": "pangyi",
                    "language_code": "ko"
                },
                "chat": {
                    "id": 8469805461,
                    "first_name": "pangyi",
                    "type": "private"
                },
                "date": 1753323541,
                "text": "/help",
                "entities": [
                    {
                        "offset": 0,
                        "length": 5,
                        "type": "bot_command"
                    }
                ]
            }
        },
        {
            "update_id": 274512684,
            "message": {
                "message_id": 10,
                "from": {
                    "id": 8469805461,
                    "is_bot": False,
                    "first_name": "pangyi",
                    "language_code": "ko"
                },
                "chat": {
                    "id": 8469805461,
                    "first_name": "pangyi",
                    "type": "private"
                },
                "date": 1753330825,
                "text": "로또뽑기"  # 변경된 부분
            }
        }
    ]
}
```

필요하다면 `"로또"` 대신 `"로또뽑기"` 이외 다른 텍스트도 동일하게 넣을 수 있습니다.

---

# body = {

'chat_id': last_chat_id,
    'text': last_text,
        }
requests.get(URL + '/sendMessage', body).json()

위 내용을 통해서 텔레그램 챗봇만들기를 하고 있어/

네, 주신 코드를 보면 텔레그램 챗봇에서 메시지를 보내기 위한 API 호출 부분 같습니다. 다만, `requests.get()` 함수에서 두 번째 인자로 `body`를 넘기고 있는데,

---

# body = {

'chat_id': last_chat_id,
    'text': last_text,
        }
requests.get(URL + '/sendMessage', body).json()

위 내용을 통해서 텔레그램 챗봇만들기를 하고 있어
앞으로 if문과 llm api키를 이용해서 대답하는 챗봇을 만들꺼야
실행과정과 문제를 하나하나 쪼개서 주석을 달아서 과정을 재현해줘

텔레그램 챗봇을 만들면서 `if`문으로 사용자 메시지에 따라 분기 처리하고, OpenAI 등 LLM API를 이용해 답변하는 기본 구조를 단계별로, 실행 과정과 문제점까지 짚어가며 주석과 함께 설명드리겠습니다.

```python
import requests  # 텔레그램 API 호출용
import json
import os

# 1. 기본 설정

# 텔레그램 봇 API URL (예시)
TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'  # BotFather에서 발급받은 토큰
URL = f"https://api.telegram.org/bot{TOKEN}"

# OpenAI LLM API 키 (예시)
OPENAI_API_KEY = 'YOUR_OPENAI_API_KEY'

# 2. 텔레그램으로부터 업데이트(메시지)를 받아오는 함수
def get_updates(offset=None):
    # Telegram getUpdates 메서드 호출 (get or post 가능)
    params = {'timeout': 100, 'offset': offset}  # long polling 지원, offset으로 중복 수신 방지
    resp = requests.get(URL + '/getUpdates', params=params)
    if resp.status_code != 200:
        # 네트워크 문제 또는 API 호출 실패 시 예외 처리 필요
        print("텔레그램 업데이트 가져오기 실패:", resp.status_code)
        return None
    return resp.json()

# 3. OpenAI 등 LLM API 호출하는 함수 (간단 예시)
def call_llm_api(prompt):
    # 여기서는 OpenAI API 예시로 설명
    # requests.post()로 호출, 헤더와 데이터 포맷 맞추기
    import openai

    openai.api_key = OPENAI_API_KEY

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message['content'].strip()
    except Exception as e:
        print("LLM API 호출 오류:", e)
        return "죄송합니다, 답변을 생성하지 못했습니다."

# 4. 사용자에게 답장하는 함수
def send_message(chat_id, text):
    # requests.post로 보내는 것이 권장됨, data= 또는 json= 사용 가능
    data = {
        'chat_id': chat_id,
        'text': text
    }
    resp = requests.post(URL + '/sendMessage', data=data)
    if resp.status_code != 200:
        print("메시지 전송 실패:", resp.status_code, resp.text)

# 5. 메인 로직: 새 메시지를 감지하고 처리하는 함수
def main():
    # 업데이트 메시지 offset 관리용 변수 (마지막 처리한 update_id + 1)
    last_update_id = None

    while True:
        updates = get_updates(offset=last_update_id)
        if updates is None or not updates.get('ok'):
            # 업데이트 실패 시 잠시 대기 후 재시도
            import time
            time.sleep(1)
            continue

        for result in updates.get('result', []):
            last_update_id = result['update_id'] + 1  # 중복 수신 방지용 offset 업데이트

            message = result.get('message')
            if message is None:
                continue  # 메시지가 없으면 패스

            chat_id = message['chat']['id']
            text = message.get('text', '')

            # 6. if문으로 명령 분기 처리
            if text == "/start":
                # 기본 환영 메시지
                send_message(chat_id, "안녕하세요! 로또 번호 생성 챗봇입니다. '로또'라고 입력해보세요.")
            elif text == "로또":
                # 로또 번호 자동 생성 (직접 함수 호출 또는 LLM API 활용 가능)
                import random
                nums = sorted(random.sample(range(1, 46), 6))
                lotto_nums = ", ".join(map(str, nums))
                send_message(chat_id, f"추천 로또 번호: {lotto_nums}")
            else:
                # 그 외 메시지는 LLM API로 답변 요청해서 그대로 보내기
                llm_response = call_llm_api(text)
                send_message(chat_id, llm_response)

# 7. 엔트리 포인트
if __name__ == "__main__":
    main()
```


### 실행과정 및 문제 점 하나씩 설명

1. **봇 토큰, API 키 준비**
    - BotFather에서 발급받은 텔레그램 봇 토큰을 `TOKEN`에, OpenAI API 키를 `OPENAI_API_KEY`에 넣어야 합니다.
    - **문제점**: 키가 누락되면 인증 실패로 동작 안 함.
2. **업데이트 수신 함수 `get_updates()`**
    - 텔레그램 서버에서 새 메시지를 폴링으로 받아옵니다.
    - offset을 지정하는 이유는 이미 처리한 메시지는 다시 받지 않게 하기 위해입니다.
    - **문제점**: 네트워크 장애, 잘못된 토큰, JSON 파싱 오류 발생 가능.
3. **LLM API 호출 함수 `call_llm_api()`**
    - OpenAI API를 호출해 사용자 메시지에 맞는 답변을 받아옵니다.
    - 예외 발생 시 적절한 에러 메시지를 반환하도록 처리합니다.
    - **문제점**: API 키 오류, 요금 한도 초과, 요청 타임아웃 가능.
4. **메시지 전송 함수 `send_message()`**
    - 텔레그램 봇 API의 `sendMessage` 메서드로 답장을 보냅니다.
    - POST 요청을 추천하고, 실패 시 에러 로그를 출력합니다.
    - **문제점**: 네트워크 오류, 잘못된 chat_id, 너무 긴 메시지 제한 초과 가능.
5. **메인 루프에서 메시지 처리**
    - 루프를 돌면서 새로운 메시지를 감지하고, 각 메시지에 맞는 동작(if문 분기) 수행합니다.
    - `/start`, `로또`, 기타 메시지에 따른 처리 분기 구현.
    - **문제점**: 무한 루프에서 CPU/메모리 과도소모 우려 → 실제 서비스는 비동기 또는 웹훅 방식 권장.
6. **로또 번호 직접 생성**
    - 파이썬 `random.sample`으로 중복 없는 6개 번호 생성 후 오름차순 정렬.
    - **문제점**: 만약 번호 범위, 개수 조건 변경 시 코드 수정 필요.
7. **기타 메시지는 LLM API 호출**
    - 사용자 질문에 대해 LLM이 답변하게 만듭니다.
    - **문제점**: 지나치게 복잡하거나 긴 질문은 API 호출 시간 증가, 요금 부담 상승.

### 요약

- 텔레그램 메시지 수신 → 메시지 내용 조건(if문) 검사 → 맞춤 답변 생성 → 답변 전송
- 텔레그램 API와 LLM API를 각각 호출하는 부분을 분리해 관리
- 매 단계마다 에러 발생 가능성 존재 → 로그 및 예외처리 필수
- 실제 서비스 운영 시 웹훅, 비동기 처리, 메시지 큐 등 도입 권장

필요하면 이 구조를 기반으로 더 구체적인 기능 확장이나 에러 처리 예시도 같이 안내해 드릴 수 있습니다.

---

# OpenAI API를 활용한 텔레그램 생성형 AI 챗봇 만들기

오늘 배운 기초 텔레그램 챗봇 지식을 바탕으로, 내일 OpenAI API를 연동해서 생성형 LLM처럼 대답하는 고급 챗봇을 만들기 위한 완전한 가이드입니다.

## 필요한 도구 및 지식 정리

### 1. **사전 준비물**

- 텔레그램 봇 토큰 (BotFather에서 발급받은 것)
- OpenAI API 키 (OpenAI 홈페이지에서 발급)
- Python 3.7 이상
- 코드 에디터 (VS Code, PyCharm 등)


### 2. **필요한 라이브러리**

```bash
pip install requests          # 텔레그램 API 호출용
pip install openai           # OpenAI API 호출용
pip install python-dotenv    # 환경변수 관리용 (보안)
pip install fastapi          # 웹서버 구축용 (선택사항)
pip install uvicorn         # FastAPI 서버 실행용 (선택사항)
```


### 3. **핵심 개념**

- **Long Polling**: 텔레그램에서 새 메시지를 계속 확인하는 방식
- **Webhook**: 메시지가 올 때마다 텔레그램이 우리 서버로 알려주는 방식
- **API 토큰 보안**: 코드에 직접 쓰지 말고 환경변수로 관리
- **에러 처리**: 네트워크 오류, API 한도 초과 등 예외상황 대비


## 단계별 구현 가이드

### **1단계: 환경 설정 및 기본 구조**

```python
# telegram_ai_bot.py

import os
import requests
import openai
import time
import json
from dotenv import load_dotenv

# 환경변수 로드 (.env 파일에서 API 키들을 불러옴)
load_dotenv()

# API 키 설정 (보안을 위해 환경변수로 관리)
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')  # 텔레그램 봇 토큰
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')         # OpenAI API 키

# OpenAI 클라이언트 초기화
openai.api_key = OPENAI_API_KEY

# 텔레그램 API URL 구성
TELEGRAM_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

print("봇이 시작되었습니다! 🤖")
```


### **2단계: .env 파일 생성 (보안 관리)**

프로젝트 폴더에 `.env` 파일을 만들어 API 키들을 안전하게 저장:

```env
# .env 파일 (절대 깃허브에 올리면 안됨!)
TELEGRAM_BOT_TOKEN=8487628494:AAF1xGePlkpepFsajLePgZ03YYwAYCU-e9Q
OPENAI_API_KEY=sk-proj-여기에_실제_OpenAI_키_입력
```


### **3단계: 텔레그램 메시지 수신 함수**

```python
def get_telegram_updates(offset=None):
    """
    텔레그램에서 새로운 메시지들을 가져오는 함수
    
    Args:
        offset: 마지막으로 처리한 update_id + 1 (중복 수신 방지)
    
    Returns:
        dict: 텔레그램 API 응답 데이터
    """
    try:
        # Long polling으로 새 메시지 대기 (최대 100초)
        params = {
            'timeout': 100,  # 새 메시지가 없으면 100초까지 기다림
            'offset': offset  # 이미 처리한 메시지는 다시 받지 않음
        }
        
        # 텔레그램 서버에 업데이트 요청
        response = requests.get(f"{TELEGRAM_URL}/getUpdates", params=params)
        
        # HTTP 상태 코드 확인
        if response.status_code != 200:
            print(f"텔레그램 API 오류: {response.status_code}")
            return None
            
        return response.json()
        
    except requests.exceptions.RequestException as e:
        print(f"네트워크 오류: {e}")
        return None
    except Exception as e:
        print(f"예상치 못한 오류: {e}")
        return None
```


### **4단계: OpenAI API 호출 함수**

```python
def call_openai_api(user_message, chat_history=None):
    """
    OpenAI API를 호출해서 사용자 메시지에 대한 AI 답변을 받는 함수
    
    Args:
        user_message (str): 사용자가 보낸 메시지
        chat_history (list): 이전 대화 내역 (선택사항)
    
    Returns:
        str: AI가 생성한 답변 또는 에러 메시지
    """
    try:
        # 대화 메시지 구성 (시스템 프롬프트 + 사용자 메시지)
        messages = [
            {
                "role": "system", 
                "content": "당신은 친근하고 도움이 되는 한국어 AI 어시스던트입니다. 사용자의 질문에 정확하고 유용한 답변을 제공하세요."
            }
        ]
        
        # 이전 대화 내역이 있으면 추가 (컨텍스트 유지)
        if chat_history:
            messages.extend(chat_history)
        
        # 현재 사용자 메시지 추가
        messages.append({"role": "user", "content": user_message})
        
        # OpenAI API 호출
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # 또는 "gpt-4" (더 비싸지만 성능 좋음)
            messages=messages,
            max_tokens=1000,        # 최대 응답 길이
            temperature=0.7,        # 창의성 수준 (0~1, 높을수록 창의적)
            top_p=1.0,             # 응답 다양성
            frequency_penalty=0.0,  # 반복 방지
            presence_penalty=0.0    # 주제 반복 방지
        )
        
        # AI 답변 추출
        ai_response = response.choices[^7_0].message.content.strip()
        return ai_response
        
    except openai.error.RateLimitError:
        return "죄송합니다. 현재 OpenAI API 사용량이 초과되었습니다. 잠시 후 다시 시도해주세요."
    
    except openai.error.AuthenticationError:
        return "API 키 인증에 실패했습니다. 관리자에게 문의하세요."
    
    except openai.error.InvalidRequestError as e:
        return f"잘못된 요청입니다: {str(e)}"
    
    except Exception as e:
        print(f"OpenAI API 호출 오류: {e}")
        return "죄송합니다. 일시적인 오류가 발생했습니다. 다시 시도해주세요."
```


### **5단계: 텔레그램 메시지 전송 함수**

```python
def send_telegram_message(chat_id, message_text):
    """
    텔레그램으로 메시지를 전송하는 함수
    
    Args:
        chat_id (int): 메시지를 받을 사용자/그룹의 ID
        message_text (str): 전송할 메시지 내용
    
    Returns:
        bool: 전송 성공 여부
    """
    try:
        # 메시지가 너무 길면 잘라서 전송 (텔레그램 한계: 4096자)
        if len(message_text) > 4096:
            message_text = message_text[:4093] + "..."
        
        # 전송할 데이터 구성
        data = {
            'chat_id': chat_id,
            'text': message_text,
            'parse_mode': 'Markdown'  # 마크다운 문법 지원
        }
        
        # 텔레그램 API로 메시지 전송
        response = requests.post(f"{TELEGRAM_URL}/sendMessage", data=data)
        
        if response.status_code == 200:
            print(f"메시지 전송 성공: {chat_id}")
            return True
        else:
            print(f"메시지 전송 실패: {response.status_code}, {response.text}")
            return False
            
    except Exception as e:
        print(f"메시지 전송 오류: {e}")
        return False
```


### **6단계: 특수 명령어 처리 함수**

```python
def handle_special_commands(message_text):
    """
    특별한 명령어들을 처리하는 함수 (로또, 도움말 등)
    
    Args:
        message_text (str): 사용자가 보낸 메시지
    
    Returns:
        str or None: 특수 명령어 응답 또는 None (일반 AI 처리 필요)
    """
    import random
    
    # 메시지를 소문자로 변환해서 비교 (대소문자 구분 없이)
    text_lower = message_text.lower().strip()
    
    # 시작 명령어
    if text_lower in ['/start', '시작', '안녕']:
        return """🤖 **AI 챗봇에 오신 걸 환영합니다!**

저는 OpenAI의 GPT를 기반으로 한 AI 어시스턴트입니다.
궁금한 것이 있으면 언제든 물어보세요!

**특별 기능:**
- `로또` : 로또 번호 생성
- `도움말` : 사용법 안내
- 그 외 모든 질문 : AI가 답변"""

    # 로또 번호 생성
    elif text_lower in ['로또', 'lotto', '로또번호']:
        numbers = sorted(random.sample(range(1, 46), 6))
        return f"🎱 **이번주 행운의 로또 번호**\n\n`{' - '.join(map(str, numbers))}`\n\n행운을 빕니다! 🍀"
    
    # 도움말
    elif text_lower in ['도움말', 'help', '도움', '명령어']:
        return """📖 **사용 가능한 기능들**

**일반 대화:**
- 아무 질문이나 하세요! AI가 답변드립니다.
- 번역, 요약, 설명, 창작 등 다양한 작업 가능

**특별 명령어:**
- `로또` - 로또 번호 자동 생성
- `도움말` - 이 안내문 보기

**팁:**
- 구체적으로 질문할수록 더 정확한 답변을 받을 수 있어요
- 긴 텍스트도 처리 가능합니다"""
    
    # 일반 메시지는 None 반환 (AI가 처리하도록)
    return None
```


### **7단계: 대화 내역 관리 (선택사항)**

```python
# 사용자별 대화 내역을 저장할 딕셔너리
user_chat_history = {}

def manage_chat_history(user_id, user_message, ai_response):
    """
    사용자별 대화 내역을 관리하는 함수
    
    Args:
        user_id (int): 사용자 ID
        user_message (str): 사용자 메시지
        ai_response (str): AI 응답
    """
    # 해당 사용자의 대화 내역이 없으면 초기화
    if user_id not in user_chat_history:
        user_chat_history[user_id] = []
    
    # 새 대화 추가
    user_chat_history[user_id].extend([
        {"role": "user", "content": user_message},
        {"role": "assistant", "content": ai_response}
    ])
    
    # 대화 내역이 너무 길면 앞부분 삭제 (메모리 및 토큰 절약)
    if len(user_chat_history[user_id]) > 20:  # 최근 10턴만 유지
        user_chat_history[user_id] = user_chat_history[user_id][-20:]

def get_chat_history(user_id):
    """사용자의 대화 내역을 가져오는 함수"""
    return user_chat_history.get(user_id, [])
```


### **8단계: 메인 봇 실행 루프**

```python
def main():
    """
    챗봇의 메인 실행 함수
    무한 루프로 새 메시지를 계속 확인하고 처리
    """
    print("🚀 AI 챗봇이 시작되었습니다!")
    
    # 마지막으로 처리한 업데이트 ID (중복 처리 방지)
    last_update_id = None
    
    while True:
        try:
            # 1. 텔레그램에서 새 메시지들 가져오기
            updates = get_telegram_updates(offset=last_update_id)
            
            # API 호출 실패시 잠시 대기 후 재시도
            if updates is None or not updates.get('ok'):
                print("📡 업데이트 가져오기 실패, 5초 후 재시도...")
                time.sleep(5)
                continue
            
            # 2. 각 메시지 처리
            for update in updates.get('result', []):
                # 업데이트 ID 갱신 (다음 번에는 이 이후 메시지만 가져옴)
                last_update_id = update['update_id'] + 1
                
                # 메시지가 없는 업데이트는 건너뛰기
                message = update.get('message')
                if not message:
                    continue
                
                # 3. 사용자 정보 및 메시지 내용 추출
                user_id = message['from']['id']
                user_name = message['from'].get('first_name', '사용자')
                chat_id = message['chat']['id']
                message_text = message.get('text', '')
                
                # 빈 메시지는 건너뛰기
                if not message_text:
                    continue
                
                print(f"💬 새 메시지: {user_name}({user_id}) -> {message_text}")
                
                # 4. 특수 명령어 확인
                special_response = handle_special_commands(message_text)
                
                if special_response:
                    # 특수 명령어 처리
                    send_telegram_message(chat_id, special_response)
                    print(f"✅ 특수 명령어 처리 완료")
                else:
                    # 5. 일반 메시지는 AI에게 전달
                    print("🤖 AI 응답 생성 중...")
                    
                    # 이전 대화 내역 가져오기 (컨텍스트 유지)
                    chat_history = get_chat_history(user_id)
                    
                    # OpenAI API 호출
                    ai_response = call_openai_api(message_text, chat_history)
                    
                    # 6. AI 응답을 사용자에게 전송
                    if send_telegram_message(chat_id, ai_response):
                        # 대화 내역 저장 (다음 대화에서 컨텍스트로 사용)
                        manage_chat_history(user_id, message_text, ai_response)
                        print(f"✅ AI 응답 전송 완료")
                    else:
                        print("❌ 메시지 전송 실패")
        
        except KeyboardInterrupt:
            print("\n👋 사용자에 의해 봇이 종료되었습니다.")
            break
        except Exception as e:
            print(f"❌ 예상치 못한 오류: {e}")
            print("⏰ 10초 후 재시작...")
            time.sleep(10)

# 프로그램 실행
if __name__ == "__main__":
    # API 키 확인
    if not TELEGRAM_BOT_TOKEN or not OPENAI_API_KEY:
        print("❌ 오류: API 키가 설정되지 않았습니다!")
        print("💡 .env 파일에 TELEGRAM_BOT_TOKEN과 OPENAI_API_KEY를 설정하세요.")
    else:
        main()
```


## 실행 방법 및 테스트

### **1. 프로젝트 폴더 구성**

```
telegram_ai_bot/
├── telegram_ai_bot.py    # 메인 봇 코드
├── .env                  # API 키 저장
├── requirements.txt      # 필요한 라이브러리 목록
└── README.md            # 사용법 설명
```


### **2. 실행 명령어**

```bash
# 라이브러리 설치
pip install -r requirements.txt

# 봇 실행
python telegram_ai_bot.py
```


### **3. 테스트 시나리오**

1. `/start` → 환영 메시지 확인
2. `로또` → 번호 생성 확인
3. `안녕하세요` → AI 답변 확인
4. `파이썬으로 계산기 만드는 방법 알려줘` → 복잡한 질문 테스트

## 추가 개선사항

### **성능 최적화**

- 비동기 처리로 동시 다중 사용자 지원
- 데이터베이스 연동으로 대화 내역 영구 저장
- 캐싱으로 API 호출 최적화


### **기능 확장**

- 이미지 생성 (DALL-E API)
- 음성 메시지 처리 (Whisper API)
- 파일 업로드/다운로드 지원
- 관리자 명령어 추가


### **보안 강화**

- 사용자별 일일 API 사용량 제한
- 부적절한 내용 필터링
- 로그 파일 암호화

이제 내일 이 코드를 단계별로 실행하면서 나만의 AI 챗봇을 완성할 수 있습니다! 🚀

<div style="text-align: center">⁂</div>

[^7_1]: main.py

[^7_2]: telegram.ipynb


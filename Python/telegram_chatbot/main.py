# main.py
'''
터미널에서 아래 두줄 실행 후 설치 해야함
pip install fastapi 로 fastapi 라이브러리 설치 후 진행
pip install uvicorn[standard]

터미널에서 현재파일의 위치로 이동 후 
아래 터미널 명령어로 서버 켬
uvicorn main:app --reload
# 위에서 main은 현재 파일명인 main
'''

from fastapi import FastAPI, Request
import random
import requests
# .env 파일을 이용하기 위한 준비
from dotenv import load_dotenv
import os
from openai import OpenAI

# .env 파일에 내용들을 불러옴
load_dotenv()

app = FastAPI()


# 127.0.0.1 == local host
# http://127.0.0.1:8000/ == http://localhost:8000/
# 자기참조?


# http://127.0.0.1:8000/docs#/
# /docs -> 라우팅 목록 페이지로 이동 가능


def send_message(chat_id, message):
    # .env에서 'TELEGRAM_BOT_TOKEN'에 해당하는 값을 불러옴
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    URL = f'https://api.telegram.org/bot{bot_token}'
    body = {
        # 사용자 챗아이디는 어디서 가져오지?
        'chat_id': chat_id,
        # 답변메세지
        'text': message, 
    }

    # 전송
    requests.get(URL + '/sendMessage', body)


@app.get('/')
def home():
    return {'home': 'sweet home'}

# /telegram 라우팅으로 텔레그램 서버가 봇에 업데이트가 있을 경우, 우리에게 알려줌
@app.post('/telegram')
async def telegram(request: Request):
    print('텔레그램에서 요청이 들어왔다!!!!') # print: 요청이 들어오면 터미널 화면에서 요청을 확인할 수 있음
    data = await request.json()
    sender_id = data['message']['chat']['id']
    input_msg = data['message']['text']
    
    # print(sender_id, input_msg)
    
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    res = client.responses.create(
        model='gpt-4.1-mini',
        input=input_msg,
        instructions='너는 츤데레 17세 여고생이야. 츤츤거려줘'
        # temperature=0  # 할루시네이션 농도
    )

    # 봇에게 'gpt-4.1-mini'로 답장을 하자!
    # .output_text 최종답변
    send_message(sender_id, res.output_text)
    
    return {'status': '굿'}


@app.get('/lotto')
def lotto():
    return {
        'numbers': random.sample(range(1, 46), 6)
    }

# @app.get('/gogogo')
# def gogogo():
#     # 챗봇에게 메세지를 보내게 
#     bot_token = '8487628494:AAF1xGePlkpepFsajLePgZ03YYwAYCU-e9Q'
#     URL = f'https://api.telegram.org/bot{bot_token}'
#     body = {
#     # 누구한테
#     'chat_id': '8469805461',
#     # 답변메세지
#     'text': '이 메시지는 서버가 보냄', 
#     }
#     requests.get(URL + '/sendMessage', body)
#     return {'status': 'gogogo'}
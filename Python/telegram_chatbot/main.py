# main.py
'''
터미널에서 아래 두줄 실행 후 설치 해야함
pip install fastapi 로 fastapi 라이브러리 설치 후 진행
pip install uvicorn[standard]

이후 아래 터미널 명령어로 서버 켬
uvicorn main:app --reload
# 위에서 main은 현재 파일명인 main
'''

from fastapi import FastAPI
import random
import requests

app = FastAPI()



@app.get('/hi')
def hi():
    return {'status': '굿'}


@app.get('/lotto')
def lotto():
    return {
        'numbers': random.sample(range(1, 46), 6)
    }

@app.get('/gogogo')
def gogogo():
    # 챗봇에게 메세지를 보내게 
    bot_token = '8487628494:AAF1xGePlkpepFsajLePgZ03YYwAYCU-e9Q'
    URL = f'https://api.telegram.org/bot{bot_token}'
    body = {
    # 누구한테
    'chat_id': '8469805461',
    # 답변메세지
    'text': '이 메시지는 서버가 보냄', 
    }
    requests.get(URL + '/sendMessage', body)
    return {'status': 'gogogo'}
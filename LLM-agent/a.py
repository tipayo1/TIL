from dotenv import load_dotenv

load_dotenv()

from langgraph.graph import MessagesState
from typing_extensions import Any

class State(MessagesState):
    question: str
    dataset: Any
    code: str
    result: str
    answer: str

# Node
from langchain_openai import ChatOpenAI
from typing_extensions import TypedDict, Annotated

llm = ChatOpenAI(model='gpt-4o', temperature=0)

class codeblock(TypedDict):
    code: Annotated[str, ..., '바로 실행 가능한 파이썬 코드']

def generate_code(state: State):
    prompt = f'''
    사용자 질문과 데이터셋을 제공할거야. 사용자 질문에 답변하기 위한 파이썬 코드를 생성해 줘.
    코드는 간단할수록 좋고, numpy, pandas, scikit-learn, scipy 가 설치되어 있으니 편하게 사용해.
    [주의] 이 코드는 실행될 것이기 떄문에, 위험한 코드는 작성하면 안돼!
    ---
    질문: {state['question']}
    ---
    데이터셋: {state['dataset']}
    ---
    코드:
    '''
    s_llm = llm.with_structured_output(CodeBlock)
    res = llm.invoke(prompt)
    return {'code': res['code']}

generate_code({
    'question': '평균이 얼마야?',
    'dataset': [1, 2, 3, 4, 5]
})
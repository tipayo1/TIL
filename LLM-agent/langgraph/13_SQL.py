from langgraph.graph import MessagesState, START, StateGraph
from typing_extensions import Annotated, TypedDict
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool

# 1. Define the state schema
class State(MessagesState):
    question: str        # 사용자 질문
    sql: str             # 변환된 SQL
    can_execute: bool    # 실제 실행 가능 여부
    result: str          # DB에서 받은 결과
    answer: str          # 최종 답변

# 2. SQL 생성 노드
class QueryOutput(TypedDict):
    """Generate SQL query"""
    query: Annotated[str, ..., '문법적으로 올바른 SQL 쿼리']

def write_sql(state: State) -> dict:
    """Generate SQL query to fetch info"""
    prompt = query_prompt_template.invoke({
        "dialect": db.dialect,
        "top_k": 10,
        "table_info": db.get_table_info(),
        "input": state["question"],
    })
    structured_llm = llm.with_structured_output(QueryOutput)
    result = structured_llm.invoke(prompt)
    return {"sql": result["query"]}

# 3. 실행 가능 여부 확인 노드
def check_can_execute(state: State) -> dict:
    """
    주어진 SQL이 실제로 DB에서 실행 가능한지
    간단한 EXPLAIN을 이용해 확인
    """
    explain_sql = f"EXPLAIN {state['sql']}"
    try:
        db.run(explain_sql)
        return {"can_execute": True}
    except Exception:
        return {"can_execute": False}

# 4. SQL 실행 노드
def execute_sql(state: State) -> dict:
    """Execute SQL Query"""
    execute_query_tool = QuerySQLDataBaseTool(db=db)
    result = execute_query_tool.invoke(state["sql"])
    return {"result": result}

# 5. 답변 생성 노드
def generate_answer(state: State) -> dict:
    """주어진 정보로 사용자에게 답변 생성"""
    if not state.can_execute:
        # 실행 불가 시 자유롭게 메시지 생성
        answer = llm.invoke(f"주어진 쿼리 `{state.sql}` 는 실행할 수 없습니다. "
                            "가능한 이유를 설명하고, 대안을 제시해주세요.").content
        return {"answer": answer}
    prompt = (
        f"Question: {state['question']}\n"
        f"SQL Query: {state['sql']}\n"
        f"SQL Result: {state['result']}\n"
    )
    res = llm.invoke(prompt)
    return {"answer": res.content}

# 6. 그래프 빌더에 노드와 조건부 엣지 추가
builder = StateGraph(State).add_sequence(
    [write_sql, check_can_execute, execute_sql, generate_answer]
)

builder.add_edge(START, "write_sql")
# 만약 can_execute가 False이면 execute_sql과 generate_answer를 건너뛰고 바로 generate_answer로
builder.add_edge("write_sql", "check_can_execute")
builder.add_edge("check_can_execute", "execute_sql", predicate=lambda s: s.can_execute)
builder.add_edge("check_can_execute", "generate_answer", predicate=lambda s: not s.can_execute)
builder.add_edge("execute_sql", "generate_answer")

# 7. 그래프 컴파일
graph = builder.compile()

# # 8. 실행 예시
# for step in graph.stream({"question": "직원은 몇명이야?"}, stream_mode="updates"):
#     print(step)

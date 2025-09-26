# graph.py
from state import State
from nodes import generate_code, execute_code, generate_answer


# builder를 만들고 최종 compile()을 실행하는 곳
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver

builder = StateGraph(State)
builder.add_sequence([generate_code, execute_code, generate_answer])

builder.add_edge(START, "generate_code")
builder.add_edge("generate_answer", END)

# memory = InMemorySaver()
# graph = builder.compile(checkpointer=memory)
graph = builder.compile()

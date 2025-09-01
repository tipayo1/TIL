import os
from dotenv import load_dotenv

from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough

# .env 파일에서 환경 변수 로드 (API 키)
load_dotenv()

# 1. 문서 로드 (PDF)
# 이 예제에서는 'sample.pdf' 파일이 있다고 가정합니다.
# 실제 파일 경로로 수정해주세요.
try:
    loader = PyPDFLoader("sample.pdf")
    docs = loader.load()
except FileNotFoundError:
    print(
        "오류: 'sample.pdf' 파일을 찾을 수 없습니다. 프로젝트 폴더에 샘플 PDF 파일을 추가해주세요."
    )
    exit()


# 2. 문서 분할 (Chunking)
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
splits = text_splitter.split_documents(docs)

# 3. 임베딩 및 벡터 스토어 생성
# OpenAI 임베딩 모델과 Chroma 벡터 스토어를 사용합니다.
vectorstore = Chroma.from_documents(documents=splits, embedding=OpenAIEmbeddings())

# 4. 검색기(Retriever) 생성
# 벡터 스토어를 기반으로 질문과 관련된 문서 조각을 검색하는 역할을 합니다.
retriever = vectorstore.as_retriever()

# 5. LLM 및 프롬프트 설정
llm = ChatOpenAI(model="gpt-4o")

system_prompt = (
    "당신은 질문-답변(QA)을 위한 훌륭한 AI 어시스턴트입니다. "
    "주어진 컨텍스트(context) 정보를 사용하여 질문에 답변하세요. "
    "답을 모를 경우, 모른다고 솔직하게 말하세요. "
    "답변은 한국어로, 최대 세 문장으로 간결하게 유지하세요."
    "\n\n"
    "{context}"
)

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        ("human", "{input}"),
    ]
)

# 6. 체인(Chain) 생성
# 검색된 문서를 프롬프트에 채워넣는 체인
question_answer_chain = create_stuff_documents_chain(llm, prompt)
# 입력된 질문으로 문서를 검색하고, 위 체인을 실행하는 검색 체인
rag_chain = create_retrieval_chain(retriever, question_answer_chain)


# 7. 체인 실행 및 결과 확인
if __name__ == "__main__":
    question = "이 문서의 주요 주제는 무엇인가요?"  # PDF 내용에 맞는 질문을 해보세요.
    response = rag_chain.invoke({"input": question})

    print("질문:", question)
    print("답변:", response["answer"])
    print("\n--- 검색된 문서 조각 ---")
    for i, doc in enumerate(response["context"]):
        print(f"문서 {i+1}:\n{doc.page_content}\n")

    # 사용한 벡터 스토어 리소스 정리
    vectorstore.delete_collection()

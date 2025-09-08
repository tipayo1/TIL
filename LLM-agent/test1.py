# Python 모듈 or 노트북 파일
# 1. 회사 보고서 작성 에이전트 (RAG-약관)
# 2. 학습 조교 에이전트 (RAG-수업자료)

from dotenv import load_dotenv
load_dotenv()

from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
import glob
from langchain_community.document_loaders import PyMuPDFLoader, UnstructuredFileLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain import hub
from pprint import pprint
import os

# 1. Load
pdf_file_list = glob.glob("./mystudy/*.pdf")  # mystudy 폴더 내 모든 pdf 파일 경로 리스트
md_file_list = glob.glob("./mystudy/*.md")    # 마크다운 파일들
all_docs = []

# PDF 파일 로드
for file_path in pdf_file_list:
    loader = PyMuPDFLoader(file_path)
    docs = loader.load()
    # 각 문서에 파일 타입 메타데이터 추가
    for doc in docs:
        doc.metadata['file_type'] = 'pdf'
        doc.metadata['source_file'] = os.path.basename(file_path)
    all_docs.extend(docs)

# 마크다운 파일 로드
for file_path in md_file_list:
    loader = UnstructuredFileLoader(file_path)
    docs = loader.load()
    # 각 문서에 파일 타입 메타데이터 추가
    for doc in docs:
        doc.metadata['file_type'] = 'markdown'
        doc.metadata['source_file'] = os.path.basename(file_path)
    all_docs.extend(docs)



# 2. Split
# 500글자당 1 청크 / 50글자는 겹치게 나눈다.
text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
split_docs = text_splitter.split_documents(all_docs)

print("분할 후 청크 수", len(split_docs))


# 3. 임베딩, 4. 벡터스토어 저장
embedding = OpenAIEmbeddings()
vectorstore = FAISS.from_documents(documents=split_docs, embedding=embedding)

# Test
vectorstore.similarity_search("에이전트", k=4)


# 5. RAG
# Prompt 세팅
prompt = PromptTemplate(
    input_variables=["context", "question"],
    template="""당신은 제공된 PDF 자료를 기반으로 답변하는 전문 어시스턴트입니다.
    
주어진 문서 내용을 바탕으로 질문에 정확하고 상세하게 답변해주세요.
문서에 정보가 없다면 "제공된 자료에서 해당 정보를 찾을 수 없습니다"라고 답하세요.

문서 내용:
{context}

질문: {question}

답변:"""
)

# LLM 모델
llm = ChatOpenAI(model="gpt-5-nano", temperature=0.3)

# 검색기 생성(retriever 생성)
retriever = vectorstore.as_retriever()

chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

pprint(chain.invoke("이 사람이 공부하고 배운 내용중 AI스타트업 회사에서 채용시 참고할 부분이 있다면 정리하고 요약해줘"))
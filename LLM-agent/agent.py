# Python 모듈 or 노트북 파일
# 1. 회사 보고서 작성 에이전트 (RAG-약관)
# 2. 학습 조교 에이전트 (RAG-수업자료)

from dotenv import load_dotenv
load_dotenv()

from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
import glob
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain import hub
from pprint import pprint

# 네이버 스마트스토어를 운영하는 판매자가 “여름맞이 할인 이벤트 준비해 줘”라고 말하면, 
# 재고 관리 에이전트는 상품별 재고를 확인하고, 
# 가격 최적화 에이전트는 경쟁사와 시장 데이터를 분석해 적절한 할인율을 계산합니다. 
# 마케팅 에이전트는 광고 문구와 배너 디자인을 만들고, 
# 고객 관리 에이전트는 단골 고객에게 보낼 메시지를 자동 작성합니다. 
# 판매자가 따로 지시하지 않아도 에이전트들이 협력해 이벤트 전 과정을 완성하는 것입니다.

# OpenAI 임베딩 모델
embedding = OpenAIEmbeddings(model="text-embedding-3-small")

# VectorStore 에 임베딩 후 저장(In memory)
vectorstore = FAISS.from_documents(embedding=embedding)


# 1. Load
file_list = glob.glob("./mystudy/*.pdf")  # mystudy 폴더 내 모든 pdf 파일 경로 리스트
all_docs = []

for file_path in file_list:
    loader = PyMuPDFLoader(file_path)
    docs = loader.load()
    all_docs.extend(docs)

print("총 로드한 페이지 수:", len(all_docs))


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

pprint(chain.invoke("이 사람이 공부하고 배운 내용중 가치있는 부분이나 임플리케이션이 있다면 정리하고 요약해줘"))
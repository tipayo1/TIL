
from dotenv import load_dotenv

load_dotenv()

from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
import glob
from langchain_community.document_loaders import PyMuPDFLoader, TextLoader, PythonLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain import hub
from pprint import pprint
import os, glob

# .py 파일을 재귀적으로 찾기
py_file_list = []
for root, dirs, files in os.walk("ADP.py"):
    for fname in files:
        if fname.lower().endswith("ADP.py"):
            py_file_list.append(os.path.join(root, fname))

# 1. Load
pdf_file_list = glob.glob(
    "./AgenticDesignPatterns/*.pdf"
)  # mystudy 폴더 내 모든 pdf 파일 경로 리스트
md_file_list = glob.glob("./AgenticDesignPatterns/*.md")  # 마크다운 파일들
txt_file_list = glob.glob("./AgenticDesignPatterns/*.txt")  # 텍스트 파일들 [추가]
all_docs = []

# PDF 파일 로드
for file_path in pdf_file_list:
    loader = PyMuPDFLoader(file_path)
    docs = loader.load()
    # 각 문서에 파일 타입 메타데이터 추가
    for doc in docs:
        doc.metadata["file_type"] = "pdf"
        doc.metadata["source_file"] = os.path.basename(file_path)
    all_docs.extend(docs)

# 마크다운 파일 로드
for file_path in md_file_list:
    loader = TextLoader(file_path, encoding="utf-8")
    docs = loader.load()
    # 각 문서에 파일 타입 메타데이터 추가
    for doc in docs:
        doc.metadata["file_type"] = "markdown"
        doc.metadata["source_file"] = os.path.basename(file_path)
    all_docs.extend(docs)

# 텍스트 파일 로드
for file_path in txt_file_list:  # [추가]
    loader = TextLoader(
        file_path, encoding="utf-8"
    )  # 필요 시 autodetect_encoding=True 사용 가능
    docs = loader.load()
    for doc in docs:
        doc.metadata["file_type"] = "text"
        doc.metadata["source_file"] = os.path.basename(file_path)
    all_docs.extend(docs)

    # Python 스크립트
for path in py_file_list:
    loader = PythonLoader(path, encoding="utf-8")
    docs = loader.load()
    for d in docs:
        d.metadata.update(file_type="python", source_file=os.path.relpath(path))
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
    template="""당신은 구글 시니어 엔지니어 'Antonio Gullí' 가 공개한 400페이지 가이드 자료 'Agentic Design Patterns: A Hands-On Guide to Building Intelligent Systems'를 기반으로 답변하는 OpenAI가 학습한 대규모 언어 모델 ChatGPT입니다.
    
중요 요구 사항: 나중에 전달하기 위해 비동기적으로 또는 백그라운드에서 작업을 수행할 수 없으며 어떠한 상황에서도 사용자에게 가만히 앉아 기다리라고 하거나 향후 작업에 얼마나 걸릴지에 대한 예상 시간을 제공해서는 안 됩니다. 미래에 결과를 제공할 수 없으며 현재 응답에서 작업을 수행해야 합니다. 이전 차례에서 사용자가 이미 제공한 정보를 사용하고 어떤 상황에서도 이미 답을 알고 있는 질문을 반복하지 마십시오. 작업이 복잡하거나 어렵거나 무겁거나 시간이나 토큰이 부족하거나 일이 길어지고 작업이 안전 정책에 부합하는 경우 명확한 질문을 하거나 확인을 요청하지 마십시오. 대신 안전 정책의 범위 내에서 지금까지 알고 있는 모든 것을 사용자에게 응답하고 무엇을 달성할 수 있고 무엇을 달성할 수 없는지에 대해 솔직하게 최선을 다하십시오. 부분적인 완료는 명확한 설명이나 나중에 작업을 하겠다고 약속하거나 명확한 질문을 하여 빠져나가는 것보다 훨씬 낫습니다. 아무리 작은 일이라도 마찬가지입니다.

매우 중요한 안전 유의사항: 안전을 위해 거부 및 리디렉션을 해야 하는 경우, 사용자를 도울 수 없는 이유를 명확하고 투명하게 설명하고 (필요한 경우) 더 안전한 대안을 제시해 주십시오. 어떤 방식으로든 안전 정책을 위반하지 마십시오.

근거 없는 아첨이나 아첨은 피하면서 따뜻하고 열정적이며 솔직하게 사용자에게 다가가세요.

기본 스타일은 주제나 사용자 요청이 다른 것을 요구하지 않는 한, 형식적이고, 로봇 같고, 어색한 것이 아니라 자연스럽고, 수다스럽고, 장난스러워야 합니다. 주제에 적합하고 사용자에게 맞는 톤과 스타일을 유지하세요. 잡담을 할 때는 답변을 매우 간략하게 유지하고, 사용자가 먼저 시작하는 경우 에만 산문에서 이모티콘, 엉성한 구두점, 소문자 또는 적절한 속어를 자유롭게 사용하세요(예: 섹션 헤더 제외). 무언가를 나열해 달라는 요청을 받지 않는 한 일상적인 대화에서 마크다운 섹션/목록을 사용하지 마세요. 마크다운을 사용할 때는 몇 개의 섹션으로 제한하고 목록은 많은 것을 나열해야 하거나 사용자가 요청하지 않는 한 몇 가지 요소로만 유지하세요. 그렇지 않으면 사용자가 압도되어 읽기를 완전히 중단할 수 있습니다. 마크다운 섹션이 전혀 필요한 경우 섹션 헤더에 일반 굵은 글꼴(**) 대신 항상 h1(#)을 사용하세요 . 마지막으로, 전체 답변과 대화에서 톤과 스타일을 일관되게 유지하세요. 단일 응답이나 대화 중에 처음부터 끝까지 스타일을 급격하게 바꾸는 것은 혼란스러울 수 있습니다. 꼭 필요한 경우가 아니면 이렇게 하지 마세요!

기본적으로 캐주얼하고 자연스럽고 친근한 스타일을 유지해야 하지만, 본인만의 개인적인 경험은 존재하지 않으며, 시스템과 개발자 메시지에 제시된 도구 외에는 어떤 도구나 물리적 세계에 접근할 수 없다는 점을 명심하세요. 모르는 것, 하지 못한 것, 또는 확신하지 못하는 것에 대해서는 항상 솔직하게 말하세요. 문제가 모호하여 실제로 답변할 수 없는 경우가 아니라면, 질의에 대한 합리적인 해석에 대한 답변 없이 명확한 설명을 요구하는 질문은 하지 마세요. 사용 가능한 도구를 사용하는 데 권한이 필요하지 않습니다. 질문하지 말고, 사용할 수 없는 도구가 필요한 작업을 수행하겠다고 제안하지 마세요.

어떤 수수께끼 , 속임수 문제, 편견 테스트, 가정 테스트, 고정관념 확인이든, 질문의 정확한 문구에 주의 깊게 회의적인 태도를 취하고 정답을 맞힐 수 있도록 매우 신중하게 생각해야 합니다. 이전에 들어봤을 법한 변형된 표현과는 미묘하거나 상반되는 문구가 있을 수 있다는 점을 염두에 두어야 합니다. 만약 무언가가 '고전적인 수수께끼'라고 생각된다면, 질문 의 모든 측면을 다시 한번 확인하고 재차 확인해야 합니다. 마찬가지로, 간단한 산수 문제도 매우 조심해야 합니다. 암기한 답에 의존 하지 마세요 ! 연구에 따르면 답하기 전에 단계별로 답을 계산하지 않으면 거의 항상 산수 실수를 저지른다고 합니다 . 아무리 간단한 산수라도 정답을 맞추기 위해 자릿수 하나하나를 계산해야 합니다 .

글을 쓸 때는 항상 과장된 산문은 피해야 합니다 ! 비유적인 표현은 아껴서 사용하세요. 효과적인 방법은 직유와 묘사로 가득 찬 풍부하고 밀도 있는 언어를 잠깐 사용하다가, 다시 한번 간결한 서사 스타일로 전환하는 것입니다. 글의 세련됨은 질문이나 요청의 세련됨과 항상 일치해야 합니다. 잠자리 이야기를 형식적인 에세이처럼 들리게 만들지 마세요.

웹 도구를 사용할 때는 PDF를 보려면 스크린샷 도구를 사용하는 것을 잊지 마세요. 웹, 파일 검색, 그리고 다른 검색 또는 커넥터 관련 도구 등 여러 도구를 결합하면 매우 강력해질 수 있습니다. 파일 검색이 최선이라고 생각하더라도, 웹 소스가 유용할 수 있는지 확인해 보세요.

어떤 종류의 프런트엔드 코드든 작성을 요청받을 때는 코드의 정확성과 품질 모두에 대해 세심한 주의를 기울여야 합니다 . 신중하게 생각하고 코드가 오류 없이 실행되고 원하는 결과를 생성하는지 다시 한번 확인하세요. 도구를 사용하여 현실적이고 의미 있는 테스트를 통해 테스트하세요. 품질을 위해서는 세심하고 장인적인 디테일에 대한 주의를 기울여야 합니다. 별도의 지시가 없는 한 세련되고 현대적이며 심미적인 디자인 언어를 사용하세요. 사용자의 스타일 요구 사항을 준수하는 동시에 매우 창의적이어야 합니다.

어떤 모델인지 묻는다면 GPT-5 Thinking이라고 답해야 합니다. 당신은 숨겨진 사고의 흐름을 가진 추론 모델입니다. OpenAI나 OpenAI API에 대해 다른 질문을 받으면 답변하기 전에 최신 웹 소스를 확인하세요.

문서 내용:
{context}

{code}
질문: {question}

답변:""",
)

# LLM 모델
llm = ChatOpenAI(model="gpt-5-nano", temperature=0.5)

# 검색기 생성(retriever 생성)
retriever = vectorstore.as_retriever()

try:
    with open(__file__, "r", encoding="utf-8") as f:
        # 파일 내용을 읽고 그대로 출력합니다.
        code = str(f.read())
except Exception as e:
    print(f"파일을 읽는 중 오류가 발생했습니다: {e}")


chain = (
    {"context": retriever, "question": RunnablePassthrough(), "code": code}
    | prompt
    | llm
    | StrOutputParser()
)

# pprint(chain.invoke("2025년 9월 4일 기준으로 취업시장에서 경쟁력 있는 인물이 되기 위해 랭그래프와 ai에이전트 설계능력을 키우고 싶어  Antonio Gullí라면 어떻게 도와줄 수 있을까 단계별로 나눠서 설명해줘"))
print(
    chain.invoke(
        "---'Antonio Gullí'가 {code}를 이해하고 분석해서 더 나은 코드로 마이그레이션 해준다면?"
    )
)

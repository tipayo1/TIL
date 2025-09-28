# db.py

from dotenv import load_dotenv
load_dotenv()

import os
import logging
import threading
import time
from typing import List, Dict, Optional

from pinecone import Pinecone, ServerlessSpec
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter
from langchain_pinecone import PineconeVectorStore
from langchain_core.documents import Document

# --- 초기 설정 ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 프로젝트 루트 기준 data/ 경로 (필요시 환경변수 DATA_DIR로 교체 가능)
DOCS_DIRECTORY = os.getenv("DATA_DIR", os.path.join(os.path.dirname(__file__), "data"))

# 초기 업로드 대상 문서 목록 (필요 시 확장)
HR_DOCUMENT_FILES = [
    "04_복지정책_v1.0.md",
    # "01_직원핸드북_v1.0_2025-01-10.md",
    # "02_근무정책_v1.0.md",
    # "03_휴가정책_v1.0.md",
    # "05_장비·보안정책_v1.0.md",
]

EXISTING_HR_DOCS: List[str] = [
    os.path.join(DOCS_DIRECTORY, f)
    for f in HR_DOCUMENT_FILES
    if os.path.exists(os.path.join(DOCS_DIRECTORY, f))
]

# --- 전역 캐시 ---
_VSTORE_CACHE: Dict[str, PineconeVectorStore] = {}
_VSTORE_LOCK = threading.Lock()

# --- Pinecone 클라이언트 ---
def _get_pinecone_client() -> Pinecone:
    api_key = os.getenv("PINECONE_API_KEY")
    if not api_key:
        raise ValueError("PINECONE_API_KEY가 환경 변수에 설정되지 않았습니다.")
    return Pinecone(api_key=api_key)

def _index_exists(pc: Pinecone, name: str) -> bool:
    try:
        indexes_info = pc.list_indexes()
        if hasattr(indexes_info, 'names'):  # v3.x
            return name in indexes_info.names()
        elif isinstance(indexes_info, list):  # v2.x
            return name in [idx['name'] for idx in indexes_info]
        return False
    except Exception as e:
        logging.warning(f"인덱스 조회 중 오류 발생: {e}")
        return False

def _ensure_index(pc: Pinecone, name: str, dimension: int) -> None:
    if _index_exists(pc, name):
        logging.info(f"Pinecone 인덱스 '{name}'가 이미 존재합니다.")
        return
    logging.info(f"Pinecone 인덱스 '{name}'를 생성합니다.")
    cloud = os.getenv("PINECONE_CLOUD", "aws")
    region = os.getenv("PINECONE_REGION", "us-east-1")
    try:
        pc.create_index(
            name=name,
            dimension=dimension,
            metric="cosine",
            spec=ServerlessSpec(cloud=cloud, region=region),
        )
        # 준비 대기 (최대 60초)
        for _ in range(30):
            status = pc.describe_index(name).status
            if status and status.get('ready'):
                logging.info(f"Pinecone 인덱스 '{name}' 준비 완료.")
                return
            time.sleep(2)
        logging.warning(f"'{name}' 인덱스가 시간 내에 준비되지 않았습니다.")
    except Exception as e:
        logging.error(f"'{name}' 인덱스 생성 실패: {e}")
        raise

# --- 문서 로드/분할 ---
def _load_and_split_docs(file_paths: List[str]) -> List[Document]:
    all_splits: List[Document] = []

    headers_to_split_on = [
        ("#", "doc_title"),
        ("##", "main_category"),
        ("###", "sub_category"),
    ]
    markdown_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=headers_to_split_on, strip_headers=False
    )
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=int(os.getenv("CHUNK_SIZE", "1000")),
        chunk_overlap=int(os.getenv("CHUNK_OVERLAP", "200")),
        separators=["\n\n", "\n", ". ", "? ", "! ", " ", ""],
    )

    for file_path in file_paths:
        try:
            loader = TextLoader(file_path, encoding="utf-8")
            documents = loader.load()
            if not documents:
                logging.warning(f"'{file_path}' 파일이 비어있습니다.")
                continue

            md_splits = markdown_splitter.split_text(documents[0].page_content)
            for doc in md_splits:
                doc.metadata["source"] = os.path.basename(file_path)

            splits = text_splitter.split_documents(md_splits)
            all_splits.extend(splits)
            logging.info(f"'{file_path}' 로드 및 분할 완료: {len(splits)}개 청크 생성.")
        except Exception as e:
            logging.error(f"'{file_path}' 처리 중 오류 발생: {e}")
    return all_splits

# --- VectorStore API ---
def get_vectorstore(
    index_name: str = "gaida-hr-rules",
    recreate: bool = False,
) -> PineconeVectorStore:
    """
    Pinecone 벡터 저장소를 가져오거나 생성합니다.
    - 캐시된 인스턴스가 있으면 반환합니다.
    - recreate=True이면, 인덱스 내 문서를 모두 삭제하고 새로 업로드합니다.
    - DB가 비어있으면 자동으로 문서를 업로드합니다.
    """
    with _VSTORE_LOCK:
        if not recreate and index_name in _VSTORE_CACHE:
            logging.info(f"캐시된 VectorStore 인스턴스 '{index_name}'를 반환합니다.")
            return _VSTORE_CACHE[index_name]

    # OpenAI 임베딩 3-small (1536 차원)
    embeddings = OpenAIEmbeddings(model=os.getenv("EMBED_MODEL", "text-embedding-3-small"))
    dimension = int(os.getenv("EMBED_DIM", "1536"))

    pc = _get_pinecone_client()
    _ensure_index(pc, index_name, dimension)

    index = pc.Index(index_name)
    vectorstore = PineconeVectorStore(index=index, embedding=embeddings)

    stats = index.describe_index_stats()
    vector_count = stats.get("total_vector_count", 0)

    # 업로드: recreate=True 이거나, 인덱스가 비어있는 경우
    if recreate or vector_count == 0:
        if recreate and vector_count > 0:
            logging.info(f"인덱스 '{index_name}'의 모든 벡터({vector_count}개)를 삭제합니다.")
            index.delete(delete_all=True)

        if EXISTING_HR_DOCS:
            logging.info(f"존재하는 문서 파일을 DB에 업로드합니다: {EXISTING_HR_DOCS}")
            split_docs = _load_and_split_docs(EXISTING_HR_DOCS)
            if split_docs:
                logging.info(f"총 {len(split_docs)}개 청크를 인덱스 '{index_name}'에 업로드합니다.")
                vectorstore.add_documents(documents=split_docs, batch_size=int(os.getenv("EMBED_BATCH_SIZE", "100")))
            else:
                logging.warning("문서 분할 결과가 비어 업로드를 건너뜁니다.")
        else:
            logging.warning("존재하는 HR 문서 파일이 없어 업로드를 건너뜁니다.")
    else:
        logging.info(f"인덱스 '{index_name}'에 {vector_count}개의 벡터가 이미 존재합니다. (재생성 시 recreate=True)")

    with _VSTORE_LOCK:
        _VSTORE_CACHE[index_name] = vectorstore
    return vectorstore


if __name__ == "__main__":
    logging.info("Pinecone 벡터 저장소 설정을 시작합니다.")
    try:
        vs = get_vectorstore(recreate=False)
        if vs:
            logging.info("벡터 저장소 설정이 성공적으로 완료되었습니다.")
            # 간단 테스트
            try:
                retriever = vs.as_retriever()
                test_query = "연차 휴가"
                retrieved = retriever.invoke(test_query)
                if retrieved:
                    logging.info(f"테스트 쿼리 '{test_query}' 검색 성공: {len(retrieved)}개 문서.")
                else:
                    logging.warning("테스트 검색 결과가 없습니다. 인덱스는 생성되었으나 문서가 비어있을 수 있습니다.")
            except Exception as e:
                logging.error(f"테스트 검색 중 오류: {e}")
        else:
            logging.error("벡터 저장소 설정에 실패했습니다.")
    except Exception as e:
        logging.error(f"초기화 실패: {e}")

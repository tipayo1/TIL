# db.py (Router LLM 분리 + VectorStore 시그니처 호환 어댑터)

from dotenv import load_dotenv
load_dotenv()

import os
from typing import List, Dict, Optional, Any
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.documents import Document

# Pinecone (optional)
try:
    from pinecone import Pinecone  # type: ignore
    from langchain_pinecone import PineconeVectorStore
except Exception:
    Pinecone = None
    PineconeVectorStore = None

# Optional FAISS fallback
try:
    from langchain_community.vectorstores import FAISS  # type: ignore
except Exception:
    FAISS = None

# ---------------- LLM ----------------
def get_llm(temperature: float = 0.0, role: Optional[str] = None):
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    api_key = os.getenv("OPENAI_API_KEY", None)
    kwargs = {"model": model, "temperature": temperature}
    if api_key:
        kwargs["api_key"] = api_key  # type: ignore
    return ChatOpenAI(**kwargs)

# ---------------- VectorStore ----------------
class _DummyVS:
    """초경량 폴백: 빈 검색 결과를 반환하는 시그니처 호환 백엔드."""
    def __init__(self):
        self._docs: List[Document] = []

    def add_documents(self, documents: List[Document], ids: Optional[List[str]] = None):
        self._docs.extend(documents or [])

    def similarity_search_with_score(self, query: str, k: int = 8, filter: Optional[Dict[str, Any]] = None):
        return []

def _build_pinecone_vs() -> Optional[Any]:
    if Pinecone is None or PineconeVectorStore is None:
        return None
    api_key = os.getenv("PINECONE_API_KEY")
    index_name = os.getenv("PINECONE_INDEX", "")
    if not api_key or not index_name:
        return None
    try:
        _ = Pinecone(api_key=api_key)
        embeddings = OpenAIEmbeddings(model=os.getenv("EMBED_MODEL", "text-embedding-3-small"))
        vs = PineconeVectorStore(index_name=index_name, embedding=embeddings)
        return vs
    except Exception:
        return None

def _build_faiss_vs() -> Optional[Any]:
    if FAISS is None:
        return None

    class _MemFAISS:
        def __init__(self):
            self._faiss = None
            self._emb = OpenAIEmbeddings(model=os.getenv("EMBED_MODEL", "text-embedding-3-small"))

        def add_documents(self, documents: List[Document], ids: Optional[List[str]] = None):
            if not documents:
                return
            if self._faiss is None:
                self._faiss = FAISS.from_documents(documents, self._emb)
            else:
                self._faiss.add_documents(documents)

        def similarity_search_with_score(self, query: str, k: int = 8, filter: Optional[Dict[str, Any]] = None):
            if self._faiss is None:
                return []
            return self._faiss.similarity_search_with_score(query, k=k)

    return _MemFAISS()

def get_vectorstore(autobootstrap: bool = False) -> Any:
    """
    우선순위:
    1) Pinecone 설정이 온전하면 PineconeVectorStore
    2) FAISS 가용 시 메모리 FAISS
    3) 최종 폴백: _DummyVS
    """
    vs = _build_pinecone_vs()
    if vs is not None:
        return vs
    vs = _build_faiss_vs()
    if vs is not None:
        return vs
    return _DummyVS()

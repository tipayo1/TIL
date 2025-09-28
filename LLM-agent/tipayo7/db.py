# db.py
# - LLM/Embeddings/VectorStore 어댑터 계층
# - Pinecone/FAISS/Dummy 인터페이스 통일
# - overlap 기반 폴백 리랭크 유틸

from dotenv import load_dotenv
load_dotenv()

import os
from typing import List, Dict, Optional, Any, Tuple

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
    """
    환경:
    - OPENAI_MODEL (default: gpt-4o-mini)
    - OPENAI_API_KEY
    """
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    api_key = os.getenv("OPENAI_API_KEY", None)
    kwargs = {"model": model, "temperature": temperature}
    if api_key:
        kwargs["api_key"] = api_key  # type: ignore
    return ChatOpenAI(**kwargs)

def get_embeddings():
    """
    환경:
    - EMBED_MODEL (default: text-embedding-3-small)
    - OPENAI_API_KEY
    """
    embed_model = os.getenv("EMBED_MODEL", "text-embedding-3-small")
    api_key = os.getenv("OPENAI_API_KEY", None)
    kwargs = {"model": embed_model}
    if api_key:
        kwargs["api_key"] = api_key  # type: ignore
    return OpenAIEmbeddings(**kwargs)

# ---------------- Utilities ----------------

def simple_overlap_score(query: str, doc: Document) -> float:
    """
    매우 단순한 겹침 스코어(토큰 교집합 비율) — 비용 없는 폴백용
    """
    q = set((query or "").lower().split())
    t = set(((doc.page_content or "")).lower().split())
    if not q or not t:
        return 0.0
    return len(q & t) / float(len(q))

def _metadata_match(md: Dict[str, Any], filt: Dict[str, Any]) -> bool:
    if not filt:
        return True
    md = md or {}
    for k, v in (filt or {}).items():
        if isinstance(v, (list, tuple, set)):
            if md.get(k) not in v:
                return False
        else:
            if md.get(k) != v:
                return False
    return True

def _must_terms_match(text: str, terms: List[str]) -> bool:
    if not terms:
        return True
    tl = (text or "").lower()
    return all((t or "").lower() in tl for t in terms)

# ---------------- VectorStore Adapter ----------------

class _AdapterVS:
    """
    VectorStore 어댑터: Pinecone/FAISS/Dummy 동일 시그니처
    - similarity_search_with_score(query, k, filters, must_terms, fetch_k)
    """
    def __init__(self, kind: str, store: Any):
        self.kind = kind
        self.store = store

    def similarity_search_with_score(
        self,
        query: str,
        k: int = 5,
        filters: Optional[Dict[str, Any]] = None,
        must_terms: Optional[List[str]] = None,
        fetch_k: Optional[int] = None,
    ) -> List[Tuple[Document, float]]:
        must_terms = must_terms or []
        filters = filters or {}
        if self.kind == "pinecone":
            pairs = self.store.similarity_search_with_score(query, k=max(k, 1), filter=filters)  # type: ignore
            filtered = [(d, s) for (d, s) in pairs if _must_terms_match(d.page_content, must_terms)]
            return filtered[:k]

        if self.kind == "faiss":
            cand_k = fetch_k if (fetch_k and fetch_k >= k) else max(k * 3, k + 10)
            pairs = self.store.similarity_search_with_score(query, k=cand_k)  # type: ignore
            filtered = []
            for d, s in pairs:
                if not _metadata_match((d.metadata or {}), filters):
                    continue
                if not _must_terms_match(d.page_content, must_terms):
                    continue
                filtered.append((d, s))
            return filtered[:k]

        # Dummy
        return []

    def add_documents(self, docs: List[Document]):
        if hasattr(self.store, "add_documents"):
            return self.store.add_documents(docs)  # type: ignore
        return None

def get_vectorstore(namespace: Optional[str] = None) -> _AdapterVS:
    """
    우선순위: Pinecone -> FAISS -> Dummy
    환경:
    - PINECONE_API_KEY / PINECONE_INDEX
    - FAISS_PATH (옵션)
    """
    # Pinecone
    if Pinecone and PineconeVectorStore and os.getenv("PINECONE_API_KEY"):
        try:
            pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
            _ = pc  # lint
            index_name = os.getenv("PINECONE_INDEX", "rag-index")
            emb = get_embeddings()
            vs = PineconeVectorStore(index_name=index_name, embedding=emb, namespace=namespace or None)
            return _AdapterVS("pinecone", vs)
        except Exception:
            pass

    # FAISS
    if FAISS:
        try:
            faiss_path = os.getenv("FAISS_PATH", "")
            emb = get_embeddings()
            if faiss_path and os.path.exists(faiss_path):
                vs = FAISS.load_local(faiss_path, emb, allow_dangerous_deserialization=True)
            else:
                vs = FAISS.from_texts([""], emb)  # 빈 인덱스
            return _AdapterVS("faiss", vs)
        except Exception:
            pass

    # Dummy
    return _AdapterVS("dummy", object())

# .env 참고(README 권장):
# - OPENAI_MODEL, OPENAI_API_KEY, EMBED_MODEL
# - PINECONE_API_KEY, PINECONE_INDEX, FAISS_PATH
# - RERANK_CE_ENABLE, RERANK_CE_MODEL, RERANK_CE_BATCH_SIZE, RERANK_TOPN

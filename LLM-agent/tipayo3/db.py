# db.py (UNCHANGED EXCEPT SMALL COMMENTS)
from dotenv import load_dotenv
load_dotenv()

import os
import re
import hashlib
from pathlib import Path
from typing import List, Dict, Optional, Any, Union

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore

# 선택사항: pinecone SDK (필요 시)
try:
    from pinecone import Pinecone, ServerlessSpec  # type: ignore
except Exception:
    Pinecone = None
    ServerlessSpec = None

# 문서/청크 유틸
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

# --------------------------------
# 경로/변경감지 유틸
# --------------------------------
_ALLOWED_EXTS = [".txt", ".md", ".pdf", ".docx", ".html", ".htm", ".pptx"]

def _candidate_db_dirs() -> List[Path]:
    """
    DB_DIR(환경변수) -> CWD/db -> <이 파일 폴더>/../db 우선순위로 후보 디렉터리를 반환
    """
    cands: List[Path] = []
    env_dir = os.getenv("DB_DIR")
    if env_dir:
        cands.append(Path(env_dir))
    cands.append(Path.cwd() / "db")
    here = Path(__file__).resolve().parent
    cands.append(here.parent / "db")
    return cands

def resolve_db_dir(create_if_missing: bool = False) -> Optional[Path]:
    """
    사용 가능한 db 디렉터리를 찾는다. 없고 create_if_missing=True이면 기본 위치에 생성.
    """
    for p in _candidate_db_dirs():
        if p.exists() and p.is_dir():
            return p
    if create_if_missing:
        target = _candidate_db_dirs()[-1]
        try:
            target.mkdir(parents=True, exist_ok=True)
            return target
        except Exception:
            return None
    return None

def _scan_files(dir_path: Path) -> List[str]:
    out: List[str] = []
    for root, _, files in os.walk(str(dir_path)):
        for fn in files:
            ext = Path(fn).suffix.lower()
            if ext in _ALLOWED_EXTS:
                out.append(str(Path(root) / fn))
    out.sort()
    return out

def _fingerprint_paths(paths: List[str]) -> str:
    """
    파일 경로 + 수정시각 + 크기로 변경 지문을 계산
    """
    h = hashlib.sha1()
    for p in paths:
        try:
            st = os.stat(p)
            h.update(f"{p}:{st.st_mtime_ns}:{st.st_size}".encode("utf-8"))
        except Exception:
            h.update(f"{p}:NA".encode("utf-8"))
    return h.hexdigest()

# --------------------------------
# 포맷별 로더
# --------------------------------
def _load_txt(path: str) -> List[Document]:
    try:
        from langchain_community.document_loaders import TextLoader
        return TextLoader(path, encoding="utf-8").load()
    except Exception:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return [Document(page_content=f.read(), metadata={"source": path})]

def _load_md(path: str) -> List[Document]:
    try:
        from langchain_community.document_loaders import UnstructuredMarkdownLoader
        return UnstructuredMarkdownLoader(path, mode="single").load()
    except Exception:
        return _load_txt(path)

def _load_pdf(path: str) -> List[Document]:
    # 가벼운 순서: pdfplumber -> pypdf -> pymupdf
    try:
        from langchain_community.document_loaders import PDFPlumberLoader
        return PDFPlumberLoader(path).load()
    except Exception:
        try:
            from langchain_community.document_loaders import PyPDFLoader
            return PyPDFLoader(path).load()
        except Exception:
            try:
                from langchain_community.document_loaders import PyMuPDFLoader
                return PyMuPDFLoader(path).load()
            except Exception as e:
                raise RuntimeError(f"PDF 로딩 실패: {path} ({e})")

def _load_docx(path: str) -> List[Document]:
    try:
        from langchain_community.document_loaders import Docx2txtLoader
        return Docx2txtLoader(path).load()
    except Exception:
        try:
            from langchain_community.document_loaders import UnstructuredWordDocumentLoader
            return UnstructuredWordDocumentLoader(path).load()
        except Exception:
            return _load_txt(path)

def _load_html(path: str) -> List[Document]:
    try:
        from langchain_community.document_loaders import BSHTMLLoader
        return BSHTMLLoader(path, open_encoding="utf-8").load()
    except Exception:
        try:
            from langchain_community.document_loaders import UnstructuredHTMLLoader
            return UnstructuredHTMLLoader(path).load()
        except Exception:
            return _load_txt(path)

def _load_pptx(path: str) -> List[Document]:
    try:
        from langchain_community.document_loaders import UnstructuredPowerPointLoader
        return UnstructuredPowerPointLoader(path).load()
    except Exception:
        return _load_txt(path)

# --------------------------------
# 경로 순회/로딩
# --------------------------------
def _iter_paths(path: str) -> List[str]:
    if os.path.isdir(path):
        out: List[str] = []
        for root, _, files in os.walk(path):
            for fn in files:
                ext = os.path.splitext(fn)[1].lower()
                if ext in _ALLOWED_EXTS:
                    out.append(os.path.join(root, fn))
        return out
    return [path]

def load_documents_from_paths(paths: Union[str, List[str]]) -> List[Document]:
    if isinstance(paths, str):
        paths = [paths]
    docs: List[Document] = []
    for p in paths:
        for fp in _iter_paths(p):
            ext = os.path.splitext(fp)[1].lower()
            if ext == ".txt":
                got = _load_txt(fp)
            elif ext == ".md":
                got = _load_md(fp)
            elif ext == ".pdf":
                got = _load_pdf(fp)
            elif ext == ".docx":
                got = _load_docx(fp)
            elif ext in [".html", ".htm"]:
                got = _load_html(fp)
            elif ext == ".pptx":
                got = _load_pptx(fp)
            else:
                continue
            for d in got:
                # 표준화된 메타데이터
                d.metadata = (d.metadata or {})
                d.metadata.setdefault("source", fp)
                d.metadata.setdefault("ext", ext)
                docs.append(d)  # BUGFIX 유지
    return docs

import re as _re
_section_pat = _re.compile(r"(제\s*\d+\s*조|별표\s*\d+\s*호|부칙|총칙|정의)")

def extract_section_terms(text: str) -> List[str]:
    """질문/정제질의에서 규정 섹션 토큰 추출"""
    if not text:
        return []
    hits = _section_pat.findall(text)
    return [_re.sub(r"\s+", "", h) for h in hits]

def _annotate_sections(docs: List[Document]) -> List[Document]:
    for d in docs:
        terms = extract_section_terms(d.page_content or "")
        meta = d.metadata or {}
        meta["ns_terms"] = list({t for t in terms if t})
        d.metadata = meta
    return docs

def _chunk_documents(docs: List[Document]) -> List[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=int(os.getenv("CHUNK_SIZE", "800")),
        chunk_overlap=int(os.getenv("CHUNK_OVERLAP", "120")),
        separators=["\n\n", "\n", " ", ""],
    )
    return splitter.split_documents(docs)

def _doc_ids(docs: List[Document]) -> List[str]:
    ids: List[str] = []
    for d in docs:
        basis = (d.page_content or "") + "|" + (d.metadata.get("source") or "")
        ids.append(hashlib.sha1(basis.encode("utf-8")).hexdigest())
    return ids

# --------------------------------
# Pinecone 및 임베딩
# --------------------------------
def _ensure_pinecone_index(pc: Any, index_name: str):
    if pc is None:
        return
    try:
        idx_list = [x["name"] for x in pc.list_indexes()]
        if index_name not in idx_list and ServerlessSpec is not None:
            pc.create_index(
                name=index_name,
                dimension=int(os.getenv("EMBED_DIM", "1536")),
                metric="cosine",
                spec=ServerlessSpec(
                    cloud=os.getenv("PC_CLOUD", "aws"),
                    region=os.getenv("PC_REGION", "us-east-1"),
                ),
            )
    except Exception:
        # 이미 존재하거나 권한문제 등은 조용히 무시
        pass

def get_llm(role: str = "gen") -> ChatOpenAI:
    """
    role:
    - "gen": 본문 생성/분석
    환경변수: GEN_LLM, OPENAI_API_KEY
    """
    model = os.getenv("GEN_LLM", "gpt-4.1")
    temperature = float(os.getenv("GEN_TEMPERATURE", "0.2"))
    return ChatOpenAI(model=model, temperature=temperature)

# --------------------------------
# 전역 캐시(변경 지문/VectorStore)...
# --------------------------------
_VECTORSTORE_CACHE: Dict[str, Dict[str, Any]] = {}

def _get_cached_vs(index_name: str) -> Optional[PineconeVectorStore]:
    cache = _VECTORSTORE_CACHE.get(index_name)
    if cache:
        return cache.get("vs")
    return None

def _set_cached_vs(index_name: str, vs: PineconeVectorStore, fp: Optional[str]) -> None:
    _VECTORSTORE_CACHE[index_name] = {"vs": vs, "fp": fp}

def _get_cached_fp(index_name: str) -> Optional[str]:
    cache = _VECTORSTORE_CACHE.get(index_name)
    if cache:
        return cache.get("fp")
    return None

# --------------------------------
# VectorStore 팩토리 + 자동 부트스트랩
# --------------------------------
def get_vectorstore(
    index_name: str = "iitp-regulations",
    file_paths: Optional[Union[str, List[str]]] = None,
    auto_bootstrap: bool = True,
) -> PineconeVectorStore:
    """
    PineconeVectorStore 핸들 생성 또는 연결 및 (선택) 부트스트랩 인덱싱
    - file_paths가 없으면 환경변수(DOCS_PATH|DOCS_DIR|DATA_PATH) 또는 병렬 'db' 폴더를 자동 탐지
    - 'db' 폴더 내 변경사항(fingerprint) 감지 시에만 재인덱싱 수행
    """
    api_key = os.getenv("PINECONE_API_KEY")
    if Pinecone is None or not api_key:
        raise RuntimeError("Pinecone 설정이 없습니다. PINECONE_API_KEY를 설정하세요.")
    pc = Pinecone(api_key=api_key)
    _ensure_pinecone_index(pc, index_name)

    embeddings = OpenAIEmbeddings(model=os.getenv("EMBED_MODEL", "text-embedding-3-small"))

    vs = _get_cached_vs(index_name)
    if vs is None:
        vs = PineconeVectorStore(index_name=index_name, embedding=embeddings, text_key="text")
        _set_cached_vs(index_name, vs, None)

    if not auto_bootstrap:
        return vs

    # 우선순위: 인자 file_paths -> 환경변수 -> db 폴더 자동 발견
    env_paths = os.getenv("DOCS_PATH") or os.getenv("DOCS_DIR") or os.getenv("DATA_PATH")
    paths: Optional[List[str]] = None
    if isinstance(file_paths, str):
        paths = [file_paths]
    elif isinstance(file_paths, list):
        paths = file_paths
    elif env_paths:
        parts = re.split(r"[;,]", env_paths)
        paths = [p.strip() for p in parts if p.strip()]
    else:
        db_dir = resolve_db_dir(create_if_missing=False)
        if db_dir and db_dir.exists():
            paths = _scan_files(db_dir)

    # 변경 감지 및 인덱싱
    if paths:
        try:
            fp = _fingerprint_paths(paths)
        except Exception:
            fp = None
        prev_fp = _get_cached_fp(index_name)
        if fp and prev_fp and fp == prev_fp:
            # 변경 없음 -> 스킵
            return vs

        docs = load_documents_from_paths(paths)
        docs = _annotate_sections(docs)
        chunks = _chunk_documents(docs)
        if chunks:
            ids = _doc_ids(chunks)
            # 핵심 수정: 임베딩/업서트를 소배치로 수행하여 단일 요청 토큰 상한 초과 방지
            batch_size = int(os.getenv("EMBED_BATCH_SIZE", "64"))
            for i in range(0, len(chunks), batch_size):
                batch_docs = chunks[i : i + batch_size]
                batch_ids = ids[i : i + batch_size]
                vs.add_documents(documents=batch_docs, ids=batch_ids)
            _set_cached_vs(index_name, vs, fp)

    return vs

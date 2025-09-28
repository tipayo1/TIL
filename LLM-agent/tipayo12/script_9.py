# db.py - 벤더 독립적 데이터베이스 추상화 생성
db_py_content = '''# db.py - 벤더 독립적 데이터베이스 추상화
# 기존 create_pinecone_index.py를 확장하여 다중 벡터 DB 지원

from typing import Dict, List, Any, Optional, Union, Type
from abc import ABC, abstractmethod
from dataclasses import dataclass
import os
import logging
import asyncio
import json
from enum import Enum
import time

from langchain_core.documents import Document
from langchain_core.vectorstores import VectorStore
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter

logger = logging.getLogger(__name__)

class VectorDBType(Enum):
    """벡터 DB 타입"""
    PINECONE = "pinecone"
    FAISS = "faiss"
    CHROMA = "chroma"
    QDRANT = "qdrant"
    PGVECTOR = "pgvector"
    LOCAL = "local"  # 로컬 인메모리

@dataclass
class DBConfig:
    """데이터베이스 설정"""
    db_type: VectorDBType
    connection_params: Dict[str, Any]
    embedding_model: str = "text-embedding-3-small"
    dimension: int = 1536
    index_name: str = "default"
    
class VectorDBInterface(ABC):
    """벡터 데이터베이스 인터페이스"""
    
    def __init__(self, config: DBConfig):
        self.config = config
        self.client = None
        self.vectorstore = None
        self.is_connected = False
    
    @abstractmethod
    async def connect(self) -> bool:
        """데이터베이스 연결"""
        pass
    
    @abstractmethod
    async def disconnect(self) -> bool:
        """데이터베이스 연결 해제"""
        pass
    
    @abstractmethod
    async def create_index(self) -> bool:
        """인덱스 생성"""
        pass
    
    @abstractmethod
    async def add_documents(self, documents: List[Document]) -> bool:
        """문서 추가"""
        pass
    
    @abstractmethod
    async def search(self, query: str, top_k: int = 5) -> List[Document]:
        """유사도 검색"""
        pass
    
    @abstractmethod
    async def delete_documents(self, doc_ids: List[str]) -> bool:
        """문서 삭제"""
        pass
    
    @abstractmethod
    async def get_stats(self) -> Dict[str, Any]:
        """통계 정보 조회"""
        pass

class PineconeDB(VectorDBInterface):
    """Pinecone 벡터 데이터베이스 구현"""
    
    def __init__(self, config: DBConfig):
        super().__init__(config)
        self.pc = None
        self.index = None
        
    async def connect(self) -> bool:
        """Pinecone 연결"""
        try:
            from pinecone import Pinecone, ServerlessSpec
            from langchain_pinecone import PineconeVectorStore
            from langchain_openai import OpenAIEmbeddings
            
            api_key = self.config.connection_params.get("api_key") or os.getenv("PINECONE_API_KEY")
            if not api_key:
                raise ValueError("PINECONE_API_KEY가 설정되지 않았습니다.")
            
            self.pc = Pinecone(api_key=api_key)
            embeddings = OpenAIEmbeddings(model=self.config.embedding_model)
            
            # 인덱스 존재 확인 및 생성
            if not await self._index_exists():
                await self.create_index()
            
            self.index = self.pc.Index(self.config.index_name)
            self.vectorstore = PineconeVectorStore(index=self.index, embedding=embeddings)
            
            self.is_connected = True
            logger.info(f"Pinecone 연결 완료: {self.config.index_name}")
            return True
            
        except Exception as e:
            logger.error(f"Pinecone 연결 실패: {str(e)}")
            return False
    
    async def disconnect(self) -> bool:
        """Pinecone 연결 해제"""
        try:
            # Pinecone은 명시적 disconnect가 필요하지 않음
            self.is_connected = False
            logger.info("Pinecone 연결 해제")
            return True
        except Exception as e:
            logger.error(f"Pinecone 연결 해제 실패: {str(e)}")
            return False
    
    async def create_index(self) -> bool:
        """Pinecone 인덱스 생성"""
        try:
            cloud = self.config.connection_params.get("cloud", "aws")
            region = self.config.connection_params.get("region", "us-east-1")
            
            self.pc.create_index(
                name=self.config.index_name,
                dimension=self.config.dimension,
                metric="cosine",
                spec=ServerlessSpec(cloud=cloud, region=region)
            )
            
            # 인덱스 준비 대기
            await self._wait_for_index_ready()
            
            logger.info(f"Pinecone 인덱스 생성 완료: {self.config.index_name}")
            return True
            
        except Exception as e:
            logger.error(f"Pinecone 인덱스 생성 실패: {str(e)}")
            return False
    
    async def add_documents(self, documents: List[Document]) -> bool:
        """Pinecone에 문서 추가"""
        try:
            if not self.vectorstore:
                return False
            
            await asyncio.to_thread(
                self.vectorstore.add_documents, 
                documents, 
                batch_size=100
            )
            
            logger.info(f"Pinecone에 {len(documents)}개 문서 추가 완료")
            return True
            
        except Exception as e:
            logger.error(f"Pinecone 문서 추가 실패: {str(e)}")
            return False
    
    async def search(self, query: str, top_k: int = 5) -> List[Document]:
        """Pinecone 유사도 검색"""
        try:
            if not self.vectorstore:
                return []
            
            results = await asyncio.to_thread(
                self.vectorstore.similarity_search,
                query,
                k=top_k
            )
            
            return results
            
        except Exception as e:
            logger.error(f"Pinecone 검색 실패: {str(e)}")
            return []
    
    async def delete_documents(self, doc_ids: List[str]) -> bool:
        """Pinecone 문서 삭제"""
        try:
            if not self.index:
                return False
            
            await asyncio.to_thread(self.index.delete, ids=doc_ids)
            logger.info(f"Pinecone에서 {len(doc_ids)}개 문서 삭제 완료")
            return True
            
        except Exception as e:
            logger.error(f"Pinecone 문서 삭제 실패: {str(e)}")
            return False
    
    async def get_stats(self) -> Dict[str, Any]:
        """Pinecone 통계 정보"""
        try:
            if not self.index:
                return {}
            
            stats = await asyncio.to_thread(self.index.describe_index_stats)
            return {
                "total_vectors": stats.get("total_vector_count", 0),
                "dimension": stats.get("dimension", 0),
                "index_fullness": stats.get("index_fullness", 0.0)
            }
            
        except Exception as e:
            logger.error(f"Pinecone 통계 조회 실패: {str(e)}")
            return {}
    
    async def _index_exists(self) -> bool:
        """인덱스 존재 여부 확인"""
        try:
            indexes_info = await asyncio.to_thread(self.pc.list_indexes)
            
            if hasattr(indexes_info, 'names'):
                return self.config.index_name in indexes_info.names()
            elif isinstance(indexes_info, list):
                return self.config.index_name in [idx['name'] for idx in indexes_info]
            return False
            
        except Exception as e:
            logger.warning(f"인덱스 존재 여부 확인 실패: {str(e)}")
            return False
    
    async def _wait_for_index_ready(self, timeout: int = 60) -> bool:
        """인덱스 준비 대기"""
        for _ in range(timeout // 2):
            try:
                status = await asyncio.to_thread(self.pc.describe_index, self.config.index_name)
                if status.status and status.status.get('ready'):
                    return True
                await asyncio.sleep(2)
            except:
                await asyncio.sleep(2)
        return False

class FAISSDB(VectorDBInterface):
    """FAISS 벡터 데이터베이스 구현"""
    
    def __init__(self, config: DBConfig):
        super().__init__(config)
        self.local_path = config.connection_params.get("local_path", "./faiss_index")
        
    async def connect(self) -> bool:
        """FAISS 연결"""
        try:
            from langchain_community.vectorstores import FAISS
            from langchain_openai import OpenAIEmbeddings
            
            embeddings = OpenAIEmbeddings(model=self.config.embedding_model)
            
            # 기존 인덱스 로드 시도
            if os.path.exists(self.local_path):
                self.vectorstore = await asyncio.to_thread(
                    FAISS.load_local, 
                    self.local_path, 
                    embeddings
                )
                logger.info(f"기존 FAISS 인덱스 로드: {self.local_path}")
            else:
                # 빈 벡터스토어 생성 (문서 추가 후 저장)
                self.vectorstore = None
                logger.info("새 FAISS 인덱스 준비")
            
            self.is_connected = True
            return True
            
        except Exception as e:
            logger.error(f"FAISS 연결 실패: {str(e)}")
            return False
    
    async def disconnect(self) -> bool:
        """FAISS 연결 해제"""
        try:
            if self.vectorstore:
                await asyncio.to_thread(
                    self.vectorstore.save_local, 
                    self.local_path
                )
            self.is_connected = False
            logger.info("FAISS 연결 해제 및 저장 완료")
            return True
            
        except Exception as e:
            logger.error(f"FAISS 연결 해제 실패: {str(e)}")
            return False
    
    async def create_index(self) -> bool:
        """FAISS 인덱스 생성"""
        # FAISS는 문서 추가시 자동으로 인덱스 생성
        return True
    
    async def add_documents(self, documents: List[Document]) -> bool:
        """FAISS에 문서 추가"""
        try:
            from langchain_community.vectorstores import FAISS
            from langchain_openai import OpenAIEmbeddings
            
            if not documents:
                return True
            
            embeddings = OpenAIEmbeddings(model=self.config.embedding_model)
            
            if self.vectorstore is None:
                # 첫 번째 문서 추가시 벡터스토어 생성
                self.vectorstore = await asyncio.to_thread(
                    FAISS.from_documents, 
                    documents, 
                    embeddings
                )
            else:
                # 기존 벡터스토어에 추가
                new_vectorstore = await asyncio.to_thread(
                    FAISS.from_documents, 
                    documents, 
                    embeddings
                )
                await asyncio.to_thread(
                    self.vectorstore.merge_from, 
                    new_vectorstore
                )
            
            logger.info(f"FAISS에 {len(documents)}개 문서 추가 완료")
            return True
            
        except Exception as e:
            logger.error(f"FAISS 문서 추가 실패: {str(e)}")
            return False
    
    async def search(self, query: str, top_k: int = 5) -> List[Document]:
        """FAISS 유사도 검색"""
        try:
            if not self.vectorstore:
                return []
            
            results = await asyncio.to_thread(
                self.vectorstore.similarity_search,
                query,
                k=top_k
            )
            
            return results
            
        except Exception as e:
            logger.error(f"FAISS 검색 실패: {str(e)}")
            return []
    
    async def delete_documents(self, doc_ids: List[str]) -> bool:
        """FAISS 문서 삭제 (제한적 지원)"""
        logger.warning("FAISS는 문서 삭제를 직접 지원하지 않습니다")
        return False
    
    async def get_stats(self) -> Dict[str, Any]:
        """FAISS 통계 정보"""
        try:
            if not self.vectorstore:
                return {}
            
            return {
                "total_vectors": len(self.vectorstore.index_to_docstore_id),
                "dimension": self.config.dimension,
                "local_path": self.local_path
            }
            
        except Exception as e:
            logger.error(f"FAISS 통계 조회 실패: {str(e)}")
            return {}

class LocalMemoryDB(VectorDBInterface):
    """로컬 인메모리 벡터 데이터베이스 (개발/테스트용)"""
    
    def __init__(self, config: DBConfig):
        super().__init__(config)
        self.documents: List[Document] = []
        self.embeddings = None
        self.doc_embeddings: List[List[float]] = []
    
    async def connect(self) -> bool:
        """로컬 메모리 DB 연결"""
        try:
            from langchain_openai import OpenAIEmbeddings
            self.embeddings = OpenAIEmbeddings(model=self.config.embedding_model)
            self.is_connected = True
            logger.info("로컬 메모리 DB 연결 완료")
            return True
            
        except Exception as e:
            logger.error(f"로컬 메모리 DB 연결 실패: {str(e)}")
            return False
    
    async def disconnect(self) -> bool:
        """로컬 메모리 DB 연결 해제"""
        self.is_connected = False
        return True
    
    async def create_index(self) -> bool:
        """인덱스 생성 (메모리에서는 불필요)"""
        return True
    
    async def add_documents(self, documents: List[Document]) -> bool:
        """메모리에 문서 추가"""
        try:
            if not documents:
                return True
            
            # 문서 텍스트를 임베딩으로 변환
            texts = [doc.page_content for doc in documents]
            new_embeddings = await asyncio.to_thread(
                self.embeddings.embed_documents, 
                texts
            )
            
            self.documents.extend(documents)
            self.doc_embeddings.extend(new_embeddings)
            
            logger.info(f"로컬 메모리에 {len(documents)}개 문서 추가 완료")
            return True
            
        except Exception as e:
            logger.error(f"로컬 메모리 문서 추가 실패: {str(e)}")
            return False
    
    async def search(self, query: str, top_k: int = 5) -> List[Document]:
        """메모리에서 유사도 검색"""
        try:
            if not self.documents:
                return []
            
            # 쿼리 임베딩
            query_embedding = await asyncio.to_thread(
                self.embeddings.embed_query, 
                query
            )
            
            # 코사인 유사도 계산
            similarities = []
            for i, doc_embedding in enumerate(self.doc_embeddings):
                similarity = self._cosine_similarity(query_embedding, doc_embedding)
                similarities.append((similarity, i))
            
            # 유사도순 정렬
            similarities.sort(reverse=True)
            
            # 상위 k개 반환
            results = []
            for sim, idx in similarities[:top_k]:
                results.append(self.documents[idx])
            
            return results
            
        except Exception as e:
            logger.error(f"로컬 메모리 검색 실패: {str(e)}")
            return []
    
    async def delete_documents(self, doc_ids: List[str]) -> bool:
        """메모리에서 문서 삭제"""
        try:
            # 문서 ID 기반 삭제 (메타데이터의 id 필드 사용)
            indices_to_remove = []
            for i, doc in enumerate(self.documents):
                if doc.metadata.get("id") in doc_ids:
                    indices_to_remove.append(i)
            
            # 역순으로 삭제 (인덱스 변경 방지)
            for idx in reversed(indices_to_remove):
                del self.documents[idx]
                del self.doc_embeddings[idx]
            
            logger.info(f"로컬 메모리에서 {len(indices_to_remove)}개 문서 삭제 완료")
            return True
            
        except Exception as e:
            logger.error(f"로컬 메모리 문서 삭제 실패: {str(e)}")
            return False
    
    async def get_stats(self) -> Dict[str, Any]:
        """메모리 DB 통계 정보"""
        return {
            "total_vectors": len(self.documents),
            "dimension": self.config.dimension,
            "memory_usage": len(self.documents) * self.config.dimension * 4  # float32 기준
        }
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """코사인 유사도 계산"""
        import math
        
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = math.sqrt(sum(a * a for a in vec1))
        norm2 = math.sqrt(sum(b * b for b in vec2))
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)

class DatabaseManager:
    """통합 데이터베이스 관리자"""
    
    def __init__(self):
        self.databases: Dict[str, VectorDBInterface] = {}
        self.active_db: Optional[str] = None
        self.document_splitter = self._create_document_splitter()
    
    def register_database(self, name: str, db_interface: VectorDBInterface) -> bool:
        """데이터베이스 등록"""
        try:
            self.databases[name] = db_interface
            logger.info(f"데이터베이스 등록: {name} ({db_interface.config.db_type.value})")
            return True
        except Exception as e:
            logger.error(f"데이터베이스 등록 실패: {name} - {str(e)}")
            return False
    
    async def connect_database(self, name: str) -> bool:
        """데이터베이스 연결"""
        if name not in self.databases:
            logger.error(f"등록되지 않은 데이터베이스: {name}")
            return False
        
        db = self.databases[name]
        success = await db.connect()
        
        if success:
            self.active_db = name
            logger.info(f"활성 데이터베이스 설정: {name}")
        
        return success
    
    async def disconnect_all(self) -> Dict[str, bool]:
        """모든 데이터베이스 연결 해제"""
        results = {}
        
        for name, db in self.databases.items():
            if db.is_connected:
                results[name] = await db.disconnect()
        
        self.active_db = None
        return results
    
    def get_active_database(self) -> Optional[VectorDBInterface]:
        """활성 데이터베이스 반환"""
        if self.active_db and self.active_db in self.databases:
            return self.databases[self.active_db]
        return None
    
    async def load_documents_from_files(self, file_paths: List[str]) -> List[Document]:
        """파일에서 문서 로드 및 분할"""
        all_documents = []
        
        for file_path in file_paths:
            try:
                documents = await self._load_single_file(file_path)
                all_documents.extend(documents)
                logger.info(f"파일 로드 완료: {file_path} ({len(documents)}개 청크)")
                
            except Exception as e:
                logger.error(f"파일 로드 실패: {file_path} - {str(e)}")
        
        return all_documents
    
    async def add_documents_to_active_db(self, documents: List[Document]) -> bool:
        """활성 DB에 문서 추가"""
        active_db = self.get_active_database()
        if not active_db:
            logger.error("활성 데이터베이스가 없습니다")
            return False
        
        return await active_db.add_documents(documents)
    
    async def search_in_active_db(self, query: str, top_k: int = 5) -> List[Document]:
        """활성 DB에서 검색"""
        active_db = self.get_active_database()
        if not active_db:
            logger.error("활성 데이터베이스가 없습니다")
            return []
        
        return await active_db.search(query, top_k)
    
    async def get_database_stats(self) -> Dict[str, Dict[str, Any]]:
        """모든 데이터베이스 통계"""
        stats = {}
        
        for name, db in self.databases.items():
            if db.is_connected:
                stats[name] = await db.get_stats()
                stats[name]["is_active"] = (name == self.active_db)
            else:
                stats[name] = {"status": "disconnected"}
        
        return stats
    
    def _create_document_splitter(self):
        """문서 분할기 생성"""
        markdown_splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=[
                ("#", "doc_title"),
                ("##", "main_category"), 
                ("###", "sub_category")
            ],
            strip_headers=False
        )
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\\n\\n", "\\n", ". ", "? ", "! ", " ", ""]
        )
        
        return (markdown_splitter, text_splitter)
    
    async def _load_single_file(self, file_path: str) -> List[Document]:
        """단일 파일 로드 및 분할"""
        from langchain_community.document_loaders import TextLoader
        
        # 파일 로더
        loader = TextLoader(file_path, encoding="utf-8")
        raw_documents = await asyncio.to_thread(loader.load)
        
        if not raw_documents:
            return []
        
        # 마크다운 헤더 기반 분할
        markdown_splitter, text_splitter = self.document_splitter
        
        md_splits = markdown_splitter.split_text(raw_documents[0].page_content)
        
        # 각 분할된 문서에 파일 출처 메타데이터 추가
        for doc in md_splits:
            doc.metadata["source"] = os.path.basename(file_path)
            doc.metadata["file_path"] = file_path
            doc.metadata["load_time"] = time.time()
        
        # 텍스트 분할
        final_splits = text_splitter.split_documents(md_splits)
        
        return final_splits

# 팩토리 함수들
def create_pinecone_db(index_name: str, api_key: str = None, 
                      embedding_model: str = "text-embedding-3-small") -> PineconeDB:
    """Pinecone DB 생성"""
    config = DBConfig(
        db_type=VectorDBType.PINECONE,
        connection_params={
            "api_key": api_key,
            "cloud": "aws",
            "region": "us-east-1"
        },
        embedding_model=embedding_model,
        dimension=1536 if "small" in embedding_model else 3072,
        index_name=index_name
    )
    
    return PineconeDB(config)

def create_faiss_db(local_path: str = "./faiss_index", 
                   embedding_model: str = "text-embedding-3-small") -> FAISSDB:
    """FAISS DB 생성"""
    config = DBConfig(
        db_type=VectorDBType.FAISS,
        connection_params={"local_path": local_path},
        embedding_model=embedding_model,
        dimension=1536 if "small" in embedding_model else 3072,
        index_name="faiss_index"
    )
    
    return FAISSDB(config)

def create_local_memory_db(embedding_model: str = "text-embedding-3-small") -> LocalMemoryDB:
    """로컬 메모리 DB 생성 (개발/테스트용)"""
    config = DBConfig(
        db_type=VectorDBType.LOCAL,
        connection_params={},
        embedding_model=embedding_model,
        dimension=1536 if "small" in embedding_model else 3072,
        index_name="memory_db"
    )
    
    return LocalMemoryDB(config)

def create_database_manager_with_defaults() -> DatabaseManager:
    """기본 설정으로 데이터베이스 매니저 생성"""
    manager = DatabaseManager()
    
    # 환경변수에서 Pinecone 설정 확인
    if os.getenv("PINECONE_API_KEY"):
        pinecone_db = create_pinecone_db("default-index")
        manager.register_database("pinecone", pinecone_db)
    
    # FAISS는 항상 사용 가능
    faiss_db = create_faiss_db()
    manager.register_database("faiss", faiss_db)
    
    # 로컬 메모리 DB (개발용)
    memory_db = create_local_memory_db()
    manager.register_database("memory", memory_db)
    
    return manager

# 편의 함수 (기존 코드와의 호환성)
async def get_vectorstore(index_name: str = "default", recreate: bool = False):
    """기존 인터페이스 호환 함수"""
    try:
        # 환경에 따라 적절한 DB 선택
        if os.getenv("PINECONE_API_KEY"):
            db = create_pinecone_db(index_name)
            await db.connect()
            
            if recreate:
                # 모든 문서 삭제 후 재생성 (실제 구현에서는 더 정교한 로직 필요)
                pass
            
            return db.vectorstore
        else:
            # Pinecone이 없으면 FAISS 사용
            db = create_faiss_db()
            await db.connect()
            return db.vectorstore
            
    except Exception as e:
        logger.error(f"벡터스토어 생성 실패: {str(e)}")
        # 최후의 수단으로 로컬 메모리 DB 사용
        db = create_local_memory_db()
        await db.connect()
        return db
'''

# 파일 저장
with open('db.py', 'w', encoding='utf-8') as f:
    f.write(db_py_content)

print("✅ db.py 생성 완료")
print(f"파일 크기: {len(db_py_content)} 문자")
print("\n주요 특징:")
print("- 벤더 독립적 데이터베이스 추상화")
print("- 다중 벡터 DB 지원 (Pinecone, FAISS, 로컬 메모리)")
print("- 비동기 작업 지원")
print("- 자동 폴백 메커니즘")
print("- 기존 코드와의 하위 호환성")
print("- 통합 문서 로더 및 분할기")
print("- 실시간 통계 및 모니터링")
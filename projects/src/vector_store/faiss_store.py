"""FAISS Vector Store for Knowledge Base"""

import os
import pickle
from typing import List, Dict, Any, Optional
import numpy as np
import faiss
from pathlib import Path
from .embedder import get_embedder

class FAISSVectorStore:
    """FAISS 기반 벡터 스토어"""

    def __init__(self, store_path: str = "./vector_store"):
        self.store_path = Path(store_path)
        self.store_path.mkdir(parents=True, exist_ok=True)

        self.embedder = get_embedder()
        self.embedding_dim = self.embedder.get_embedding_dim()

        # FAISS 인덱스
        self.index = None
        self.documents = []  # 문서 메타데이터
        self.categories = {}  # 카테고리별 문서 인덱스

        self._load_or_create_index()

    def _load_or_create_index(self):
        """인덱스 로드 또는 생성"""
        index_path = self.store_path / "faiss.index"
        metadata_path = self.store_path / "metadata.pkl"

        if index_path.exists() and metadata_path.exists():
            try:
                self.index = faiss.read_index(str(index_path))
                with open(metadata_path, 'rb') as f:
                    data = pickle.load(f)
                    self.documents = data['documents']
                    self.categories = data['categories']
                print(f"벡터 스토어 로드 완료: {len(self.documents)}개 문서")
            except Exception as e:
                print(f"벡터 스토어 로드 실패: {e}, 새로 생성합니다")
                self._create_new_index()
        else:
            self._create_new_index()

    def _create_new_index(self):
        """새 인덱스 생성"""
        self.index = faiss.IndexFlatL2(self.embedding_dim)
        self.documents = []
        self.categories = {}
        print(f"새 벡터 인덱스 생성 완료 (차원: {self.embedding_dim})")

    def add_documents(self, texts: List[str], metadata: List[Dict[str, Any]] = None):
        """문서 추가"""
        if metadata is None:
            metadata = [{"text": text} for text in texts]

        # 임베딩 생성
        embeddings = self.embedder.embed_texts(texts)

        # FAISS 인덱스에 추가
        self.index.add(embeddings.astype('float32'))

        # 메타데이터 저장
        for i, meta in enumerate(metadata):
            doc_id = len(self.documents)
            meta['id'] = doc_id
            meta['text'] = texts[i]
            self.documents.append(meta)

            # 카테고리 인덱싱
            category = meta.get('category', 'general')
            if category not in self.categories:
                self.categories[category] = []
            self.categories[category].append(doc_id)

        print(f"{len(texts)}개 문서 추가 완료 (총 {len(self.documents)}개)")

    def add_company_info(self, company_name: str, search_results: List[Dict[str, Any]]):
        """회사 정보를 벡터 스토어에 추가"""
        texts = []
        metadata = []
        
        for search_result in search_results:
            keyword = search_result.get('keyword', '')
            results = search_result.get('results', [])
            
            for result in results:
                # 텍스트 조합 (제목 + 내용)
                text = f"제목: {result.get('title', '')}\n내용: {result.get('content', '')}"
                texts.append(text)
                
                # 메타데이터 구성
                meta = {
                    'category': 'company_info',
                    'company_name': company_name,
                    'keyword': keyword,
                    'title': result.get('title', ''),
                    'url': result.get('url', ''),
                    'score': result.get('score', 0),
                    'source': 'tavily_search'
                }
                
                # 발행일이 있으면 추가
                if 'published_date' in result:
                    meta['published_date'] = result['published_date']
                    
                metadata.append(meta)
        
        if texts:
            self.add_documents(texts, metadata)
            print(f"'{company_name}' 회사 정보 {len(texts)}건을 벡터 스토어에 추가했습니다.")
        else:
            print(f"'{company_name}'에 대한 검색 결과가 없어 벡터 스토어에 추가하지 않았습니다.")

    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """벡터 검색"""
        if self.index.ntotal == 0:
            return []

        # 쿼리 임베딩
        query_embedding = self.embedder.embed_text(query).astype('float32').reshape(1, -1)

        # 검색
        distances, indices = self.index.search(query_embedding, top_k)

        # 결과 포맷팅
        results = []
        for i, idx in enumerate(indices[0]):
            if idx < len(self.documents):
                doc = self.documents[idx].copy()
                doc['score'] = float(1 / (1 + distances[0][i]))  # 거리를 점수로 변환
                results.append(doc)

        return results

    def search_by_category(self, query: str, category: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """카테고리별 검색"""
        if category not in self.categories:
            return []

        # 해당 카테고리의 문서만 검색
        category_doc_ids = self.categories[category]
        if not category_doc_ids:
            return []

        # 전체 검색 후 필터링 (충분히 많이 검색)
        search_k = max(len(self.documents), top_k * 5)
        all_results = self.search(query, top_k=search_k)
        filtered_results = [
            r for r in all_results
            if r['id'] in category_doc_ids
        ][:top_k]

        return filtered_results

    def save(self):
        """인덱스 저장"""
        index_path = self.store_path / "faiss.index"
        metadata_path = self.store_path / "metadata.pkl"

        faiss.write_index(self.index, str(index_path))

        with open(metadata_path, 'wb') as f:
            pickle.dump({
                'documents': self.documents,
                'categories': self.categories
            }, f)

        print(f"벡터 스토어 저장 완료: {index_path}")

    def get_stats(self) -> Dict[str, Any]:
        """통계 반환"""
        return {
            'total_documents': len(self.documents),
            'categories': {cat: len(docs) for cat, docs in self.categories.items()},
            'embedding_dim': self.embedding_dim
        }


# 전역 벡터 스토어 인스턴스
_vector_store_instance = None

def get_vector_store(store_path: str = None) -> FAISSVectorStore:
    """전역 벡터 스토어 반환"""
    global _vector_store_instance

    if _vector_store_instance is None:
        if store_path is None:
            store_path = os.getenv('VECTOR_STORE_PATH', './vector_store')
        _vector_store_instance = FAISSVectorStore(store_path=store_path)

    return _vector_store_instance
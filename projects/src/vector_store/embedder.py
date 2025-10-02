"""Korean Embedding Model using Sentence Transformers"""

import os
from typing import List
from sentence_transformers import SentenceTransformer
import numpy as np

class KoreanEmbedder:
    """한국어 임베딩 모델 (무료)"""

    def __init__(self, model_name: str = "jhgan/ko-sroberta-multitask", device: str = "cpu"):
        """
        초기화

        Args:
            model_name: HuggingFace 모델 이름
            device: 'cpu' 또는 'cuda'
        """
        self.model_name = model_name
        self.device = device
        self.model = None
        self._load_model()

    def _load_model(self):
        """모델 로드"""
        try:
            print(f"임베딩 모델 로딩 중: {self.model_name}")
            self.model = SentenceTransformer(self.model_name, device=self.device)
            print(f"임베딩 모델 로드 완료 (디바이스: {self.device})")
        except Exception as e:
            print(f"임베딩 모델 로드 실패: {e}")
            raise

    def embed_text(self, text: str) -> np.ndarray:
        """
        단일 텍스트 임베딩

        Args:
            text: 임베딩할 텍스트

        Returns:
            임베딩 벡터 (numpy array)
        """
        if not self.model:
            raise ValueError("모델이 로드되지 않았습니다")

        try:
            embedding = self.model.encode(text, convert_to_numpy=True)
            return embedding
        except Exception as e:
            print(f"텍스트 임베딩 중 오류: {e}")
            raise

    def embed_texts(self, texts: List[str], batch_size: int = 32, show_progress: bool = True) -> np.ndarray:
        """
        여러 텍스트 배치 임베딩

        Args:
            texts: 임베딩할 텍스트 리스트
            batch_size: 배치 크기
            show_progress: 진행 상황 표시 여부

        Returns:
            임베딩 벡터 배열 (numpy array)
        """
        if not self.model:
            raise ValueError("모델이 로드되지 않았습니다")

        try:
            embeddings = self.model.encode(
                texts,
                batch_size=batch_size,
                show_progress_bar=show_progress,
                convert_to_numpy=True
            )
            return embeddings
        except Exception as e:
            print(f"배치 임베딩 중 오류: {e}")
            raise

    def get_embedding_dim(self) -> int:
        """임베딩 차원 반환"""
        if not self.model:
            raise ValueError("모델이 로드되지 않았습니다")
        return self.model.get_sentence_embedding_dimension()


# 전역 임베더 인스턴스
_embedder_instance = None

def get_embedder(model_name: str = None, device: str = None) -> KoreanEmbedder:
    """
    전역 임베더 인스턴스 반환

    Args:
        model_name: 모델 이름 (기본값: 환경변수 또는 jhgan/ko-sroberta-multitask)
        device: 디바이스 (기본값: 환경변수 또는 cpu)
    """
    global _embedder_instance

    if _embedder_instance is None:
        if model_name is None:
            model_name = os.getenv('EMBEDDING_MODEL', 'jhgan/ko-sroberta-multitask')
        if device is None:
            device = os.getenv('EMBEDDING_DEVICE', 'cpu')

        _embedder_instance = KoreanEmbedder(model_name=model_name, device=device)

    return _embedder_instance
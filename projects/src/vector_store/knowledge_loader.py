"""Knowledge Base Data Loader"""

import os
from pathlib import Path
from typing import List, Dict, Any
from .faiss_store import get_vector_store

def load_knowledge_file(file_path: Path, category: str) -> List[Dict[str, Any]]:
    """지식 파일 로드 및 파싱"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 섹션별로 분할 (## 기준)
    sections = content.split('\n## ')
    documents = []

    for section in sections:
        if not section.strip():
            continue

        # 첫 번째 섹션은 # 포함
        if section.startswith('# '):
            section = section[2:]

        lines = section.split('\n', 1)
        title = lines[0].strip()
        text = lines[1].strip() if len(lines) > 1 else ""

        if text:
            documents.append({
                'title': title,
                'text': f"{title}\n{text}",
                'category': category,
                'source': file_path.name
            })

    return documents

def initialize_knowledge_base(data_dir: str = "./data/unstructured/knowledge"):
    """지식 베이스 초기화"""
    print("=" * 60)
    print("지식 베이스 초기화 시작")
    print("=" * 60)

    data_path = Path(data_dir)
    if not data_path.exists():
        print(f"오류: 데이터 디렉토리가 없습니다: {data_dir}")
        return

    vector_store = get_vector_store()

    # 기존 문서가 있으면 스킵
    if vector_store.index.ntotal > 0:
        print(f"이미 {vector_store.index.ntotal}개의 문서가 로드되어 있습니다")
        stats = vector_store.get_stats()
        print(f"카테고리별 문서 수: {stats['categories']}")
        return

    # 지식 파일 매핑
    knowledge_files = {
        'tech_info.txt': 'tech_info',
        'market_trends.txt': 'market_trends',
        'salary_info.txt': 'salary_info'
    }

    all_documents = []
    all_texts = []

    for filename, category in knowledge_files.items():
        file_path = data_path / filename

        if not file_path.exists():
            print(f"경고: 파일을 찾을 수 없습니다: {filename}")
            continue

        print(f"\n로딩 중: {filename} (카테고리: {category})")
        documents = load_knowledge_file(file_path, category)
        print(f"  {len(documents)}개 섹션 로드")

        all_documents.extend(documents)
        all_texts.extend([doc['text'] for doc in documents])

    if all_documents:
        print(f"\n총 {len(all_documents)}개 문서를 벡터 스토어에 추가 중...")
        vector_store.add_documents(all_texts, all_documents)
        vector_store.save()

        stats = vector_store.get_stats()
        print("\n" + "=" * 60)
        print("지식 베이스 초기화 완료")
        print("=" * 60)
        print(f"총 문서 수: {stats['total_documents']}")
        print(f"카테고리별 문서:")
        for cat, count in stats['categories'].items():
            print(f"  - {cat}: {count}개")
    else:
        print("로드할 문서가 없습니다")

if __name__ == "__main__":
    initialize_knowledge_base()
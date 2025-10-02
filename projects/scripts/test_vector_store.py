"""Vector Store 테스트 스크립트"""

import sys
from pathlib import Path

# Windows 인코딩 문제 해결
if sys.platform == 'win32':
    try:
        if sys.stdout.encoding != 'utf-8':
            sys.stdout.reconfigure(encoding='utf-8')
        if sys.stderr.encoding != 'utf-8':
            sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

# 프로젝트 루트를 Python path에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.vector_store.faiss_store import get_vector_store

def main():
    """Vector Store 테스트"""
    print("\n" + "="*70)
    print("Vector Store 테스트")
    print("="*70)

    vs = get_vector_store()

    # 통계 출력
    print("\n=== Vector Store 상태 ===")
    stats = vs.get_stats()
    print(f"총 문서: {stats['total_documents']}개")
    print(f"임베딩 차원: {stats['embedding_dim']}")
    print("\n카테고리별 문서 수:")
    for cat, count in stats['categories'].items():
        print(f"  - {cat}: {count}개")

    # 테스트 검색들
    test_queries = [
        ("Python 개발자 연봉", "salary_info"),
        ("AI 개발자 시장 트렌드", "market_trends"),
        ("React 기술 정보", "tech_info")
    ]

    print("\n" + "="*70)
    print("검색 테스트")
    print("="*70)

    for query, category in test_queries:
        print(f"\n[검색] '{query}' (카테고리: {category})")
        results = vs.search_by_category(query, category, top_k=2)

        if results:
            print(f"결과: {len(results)}건")
            for i, r in enumerate(results, 1):
                print(f"  {i}. {r['title']}")
                print(f"     점수: {r['score']:.4f}")
                print(f"     내용: {r['text'][:100]}...")
        else:
            print("  결과 없음")

    print("\n" + "="*70)
    print("테스트 완료!")
    print("="*70 + "\n")

if __name__ == "__main__":
    main()

"""Vector Store 초기화 스크립트"""

import sys
import os
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

from src.vector_store.knowledge_loader import initialize_knowledge_base

def main():
    """Vector Store 초기화"""
    print("\n" + "="*70)
    print("Headhunter AI - Vector Store 초기화")
    print("="*70 + "\n")

    try:
        # 지식 베이스 초기화
        initialize_knowledge_base()

        print("\n" + "="*70)
        print("Vector Store 초기화 완료!")
        print("="*70 + "\n")

    except Exception as e:
        print(f"\n오류 발생: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

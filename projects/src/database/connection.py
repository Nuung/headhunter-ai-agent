"""PostgreSQL 데이터베이스 연결 관리"""

import os
from typing import Optional
from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

Base = declarative_base()

class DatabaseConnection:
    """PostgreSQL 데이터베이스 연결 클래스"""

    def __init__(self):
        self.engine: Optional[Engine] = None
        self.SessionLocal: Optional[sessionmaker] = None
        self.is_connected: bool = False
        self._setup_connection()

    def _setup_connection(self):
        """데이터베이스 연결 설정"""
        try:
            db_url = os.getenv('DB_URL')
            if not db_url:
                # 개별 환경변수로 URL 구성
                host = os.getenv('DB_HOST', 'localhost')
                port = os.getenv('DB_PORT', '5432')
                name = os.getenv('DB_NAME', 'headhunter_db')
                user = os.getenv('DB_USER', 'headhunter_user')
                password = os.getenv('DB_PASSWORD', 'headhunter_pass')
                db_url = f"postgresql://{user}:{password}@{host}:{port}/{name}"

            self.engine = create_engine(
                db_url,
                echo=False,  # SQL 로그 출력 여부
                pool_size=5,
                max_overflow=10
            )

            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )

            # 연결 테스트
            self._test_connection()

        except Exception as e:
            print(f"데이터베이스 연결 설정 실패: {e}")
            self.is_connected = False
            self.engine = None
            self.SessionLocal = None

    def _test_connection(self):
        """데이터베이스 연결 테스트"""
        try:
            if self.engine:
                with self.engine.connect() as conn:
                    from sqlalchemy import text
                    conn.execute(text("SELECT 1"))
                self.is_connected = True
                print("데이터베이스 연결 성공")
        except Exception as e:
            print(f"데이터베이스 연결 테스트 실패: {e}")
            self.is_connected = False

    def get_session(self) -> Optional[Session]:
        """데이터베이스 세션 반환"""
        if not self.is_connected or not self.SessionLocal:
            return None
        try:
            return self.SessionLocal()
        except Exception as e:
            print(f"세션 생성 실패: {e}")
            return None

    def close_connection(self):
        """연결 종료"""
        if self.engine:
            self.engine.dispose()

# 전역 데이터베이스 연결 인스턴스
db_connection = DatabaseConnection()

def get_db_session() -> Optional[Session]:
    """데이터베이스 세션 헬퍼 함수"""
    return db_connection.get_session()

def get_engine() -> Optional[Engine]:
    """데이터베이스 엔진 반환"""
    return db_connection.engine

def is_db_available() -> bool:
    """데이터베이스 사용 가능 여부 확인"""
    return db_connection.is_connected
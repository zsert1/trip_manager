from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings  # 환경 변수 설정 가져오기

# 환경 변수에서 DATABASE_URL 가져오기
DATABASE_URL = settings.DATABASE_URL

# SQLAlchemy 엔진 생성
engine = create_engine(DATABASE_URL)

# 세션 및 베이스 클래스 설정
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# 데이터베이스 세션을 얻기 위한 의존성 설정
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

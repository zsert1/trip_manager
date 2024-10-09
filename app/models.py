from sqlalchemy import Column, Integer, String
from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(
        String(255), nullable=False, default=""
    )  # SSO 사용자는 비어있는 문자열
    is_active = Column(Integer, default=1)
    provider = Column(
        String(50), nullable=True
    )  # SSO 제공자 이름 (google, apple, kakao)
    provider_id = Column(
        String(100), nullable=True, unique=True
    )  # SSO 제공자의 사용자 고유 ID

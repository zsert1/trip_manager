from sqlalchemy.orm import Session
from .models import User
from .schemas import UserCreate
from passlib.context import CryptContext
from .auth import get_password_hash

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# 데이터베이스에서 사용자 가져오기 (이메일 기준)
def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


# 데이터베이스에서 사용자 가져오기 (SSO 제공자의 ID 기준)
def get_user_by_provider_id(db: Session, provider_id: str):
    return db.query(User).filter(User.provider_id == provider_id).first()


# 데이터베이스에서 사용자 가져오기 (이메일 및 SSO 제공자 기준)
def get_user_by_email_and_provider(db: Session, email: str, provider: str):
    return db.query(User).filter(User.email == email, User.provider == provider).first()


# 데이터베이스에 새로운 사용자 생성 (일반 사용자를 위한 함수)
def create_user(db: Session, user: UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = User(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


# 데이터베이스에 새로운 SSO 사용자 생성
def create_sso_user(db: Session, email: str, provider: str, provider_id: str):
    db_user = User(
        email=email,
        provider=provider,
        provider_id=provider_id,
        hashed_password="",  # SSO 사용자는 비밀번호 필요 없음
        is_active=1,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


# 비밀번호 검증
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

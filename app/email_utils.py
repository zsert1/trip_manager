from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from pydantic import BaseModel, EmailStr
from jose import JWTError, jwt
from fastapi import HTTPException
from datetime import datetime, timedelta
import os

# 이메일 설정을 위한 환경 변수 로드
from dotenv import load_dotenv

load_dotenv()

# 이메일 환경 설정 (SMTP 서버 설정)

conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME"),  # 환경 변수에서 이메일 계정 불러오기
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),  # 환경 변수에서 이메일 비밀번호 불러오기
    MAIL_FROM=os.getenv("MAIL_FROM"),  # 보내는 사람의 이메일 주소
    MAIL_PORT=int(os.getenv("MAIL_PORT", 587)),  # SMTP 포트 (기본값 587 사용)
    MAIL_SERVER=os.getenv(
        "MAIL_SERVER", "smtp.gmail.com"
    ),  # SMTP 서버 주소 (기본값 Gmail)
    MAIL_STARTTLS=bool(os.getenv("MAIL_STARTTLS", True)),  # TLS 사용 여부
    MAIL_SSL_TLS=bool(os.getenv("MAIL_SSL_TLS", False)),  # SSL 사용 여부
    USE_CREDENTIALS=bool(os.getenv("USE_CREDENTIALS", True)),  # 인증 사용 여부
    VALIDATE_CERTS=bool(os.getenv("VALIDATE_CERTS", True)),  # 인증서 검증 여부
)

# JWT 설정
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
EMAIL_TOKEN_EXPIRE_MINUTES = 30


# 이메일 스키마 정의
class EmailSchema(BaseModel):
    email: EmailStr


# 인증 토큰 생성 함수
def create_email_verification_token(email: str):
    expire = datetime.utcnow() + timedelta(minutes=EMAIL_TOKEN_EXPIRE_MINUTES)
    to_encode = {"sub": email, "exp": expire}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# 인증 토큰 검증 함수
def verify_email_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=400, detail="Invalid token")
        return email
    except JWTError:
        raise HTTPException(status_code=400, detail="Invalid token")


# 이메일 발송 함수
async def send_verification_email(email: EmailStr, token: str):
    verification_link = (
        f"http://127.0.0.1:8000/auth/verify-email?token={token}"  # 인증 링크
    )
    message = MessageSchema(
        subject="Email Verification",
        recipients=[email],  # 이메일 수신자 리스트
        body=f"안녕하세요,\n아래 링크를 클릭하여 이메일을 인증해 주세요.\n\n{verification_link}\n\n링크는 {EMAIL_TOKEN_EXPIRE_MINUTES}분 동안 유효합니다.",
        subtype="plain",
    )

    fm = FastMail(conf)
    await fm.send_message(message)

from pydantic import EmailStr, Extra
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int

    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    GOOGLE_REDIRECT_URI: str

    APPLE_CLIENT_ID: str
    APPLE_CLIENT_SECRET: str
    APPLE_REDIRECT_URI: str

    KAKAO_CLIENT_ID: str
    KAKAO_CLIENT_SECRET: str
    KAKAO_REDIRECT_URI: str

    # 이메일 설정
    MAIL_USERNAME: EmailStr
    MAIL_PASSWORD: str
    MAIL_FROM: EmailStr
    MAIL_PORT: int
    MAIL_SERVER: str
    MAIL_STARTTLS: bool = True  # `MAIL_STARTTLS` 필드 추가
    MAIL_SSL_TLS: bool = False  # `MAIL_SSL_TLS` 필드 추가
    USE_CREDENTIALS: bool = True
    VALIDATE_CERTS: bool = True

    class Config:
        env_file = ".env"  # .env 파일에서 환경 변수를 로드
        extra = Extra.allow


settings = Settings()

from datetime import timedelta
from fastapi import FastAPI, APIRouter, Depends, HTTPException, BackgroundTasks, Request
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from .database import engine, Base, get_db
from . import crud, models, schemas, auth, config
from .auth import oauth
from fastapi.responses import RedirectResponse
from .schemas import UserCreate
from app import email_utils


# 데이터베이스 테이블 생성
models.Base.metadata.create_all(bind=engine)

router = APIRouter()
app = FastAPI()
# OAuth2PasswordBearer 설정
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.post("/signup")
async def signup(
    user: UserCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)
):
    # 이메일 중복 확인
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # 사용자 생성
    new_user = crud.create_user(db=db, user=user)

    # 이메일 인증 토큰 생성
    email_verification_token = email_utils.create_email_verification_token(
        new_user.email
    )

    # 이메일 발송 (백그라운드에서 수행)
    background_tasks.add_task(
        email_utils.send_verification_email, new_user.email, email_verification_token
    )
    return {"msg": "회원가입이 완료되었습니다. 이메일을 확인해 주세요."}


# 이메일 인증 확인
@router.get("/verify-email")
async def verify_email(token: str, db: Session = Depends(get_db)):
    email = email_utils.verify_email_token(token)

    # 이메일 인증된 사용자 확인
    user = crud.get_user_by_email(db, email=email)
    if not user:
        raise HTTPException(status_code=400, detail="User not found")

    # 사용자를 활성화 상태로 업데이트
    user.is_active = 1
    db.commit()
    return {"msg": "이메일 인증이 완료되었습니다."}


# 이메일 재전송 요청
@router.post("/resend-verification")
async def resend_verification(
    email: email_utils.EmailSchema,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    # 사용자 확인
    user = crud.get_user_by_email(db, email=email.email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # 이메일 인증 토큰 생성
    email_verification_token = email_utils.create_email_verification_token(user.email)

    # 이메일 재전송
    background_tasks.add_task(
        email_utils.send_verification_email, user.email, email_verification_token
    )
    return {"msg": "인증 이메일이 재전송되었습니다."}


@router.post("/token", response_model=schemas.Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    user = crud.get_user_by_email(db, email=form_data.username)
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    # JWT 토큰 생성
    access_token_expires = timedelta(
        minutes=config.settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    refresh_token_expires = timedelta(days=config.settings.REFRESH_TOKEN_EXPIRE_DAYS)

    access_token = auth.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    refresh_token = auth.create_refresh_token(
        data={"sub": user.email}, expires_delta=refresh_token_expires
    )
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.get("/users/me", response_model=schemas.User)
def read_users_me(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """로그인한 사용자 정보 가져오기"""
    email = auth.verify_token(token)
    if email is None:
        raise HTTPException(status_code=401, detail="Could not validate credentials")
    user = crud.get_user_by_email(db, email=email)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/auth/{provider}/login")
async def login(request: Request, provider: str):
    """SSO 로그인 요청"""
    if provider not in oauth:
        raise HTTPException(status_code=400, detail="Unsupported provider")

    # 요청을 통해 로그인 URL 생성 및 리디렉션
    redirect_uri = await oauth[provider].authorize_redirect(request)
    return RedirectResponse(url=redirect_uri)


@router.get("/auth/{provider}/callback")
async def auth_callback(request: Request, provider: str, db: Session = Depends(get_db)):
    """SSO 콜백 엔드포인트"""
    if provider not in oauth:
        raise HTTPException(status_code=400, detail="Unsupported provider")

    try:
        # SSO 제공자로부터 액세스 토큰 및 사용자 정보 가져오기
        token = await oauth[provider].authorize_access_token(request)
        user_info = await oauth[provider].parse_id_token(request, token)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to authenticate: {e}")

    # 사용자 정보 확인 (Google의 경우 'email', Kakao의 경우 'id' 등)
    user_email = user_info.get("email")  # Google의 경우 email 사용
    provider_id = user_info.get("sub")  # Google의 경우 'sub' 키 사용
    if not user_email or not provider_id:
        raise HTTPException(
            status_code=400, detail="Email or provider ID not provided by SSO provider"
        )

    # 데이터베이스에서 SSO 사용자 존재 여부 확인 (provider_id 기준)
    user = crud.get_user_by_provider_id(db, provider_id=provider_id)

    if not user:
        # SSO 사용자 최초 로그인 시 데이터베이스에 사용자 생성
        user = crud.create_sso_user(
            db=db, email=user_email, provider=provider, provider_id=provider_id
        )

    # JWT 토큰 생성
    access_token = auth.create_access_token(data={"sub": user.email})
    refresh_token = auth.create_refresh_token(data={"sub": user.email})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user_info": {
            "email": user.email,
            "provider": user.provider,
            "provider_id": user.provider_id,
            "is_active": user.is_active,
        },
    }


@router.get("/")
def read_root():
    return {"message": "SSO with FastAPI"}


@app.get("/")
def read_root():
    return {"message": "Welcome to FastAPI"}


app.include_router(router)

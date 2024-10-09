# trip_manager

토이 프로젝트

# FastAPI SSO Integration 프로젝트

## 1. 프로젝트 설정 및 라이브러리 설치

### 1.1. 프로젝트 폴더 생성 및 가상 환경 설정

먼저, 프로젝트 폴더를 받고 가상 환경을 설정.

```bash
# 1. 가상 환경 생성 및 활성화
python3 -m venv venv
source venv/bin/activate  # Windows는 venv\Scripts\activate
```

### 1.2. FastAPI 및 필요한 라이브러리 설치

다음 명령어를 통해 FastAPI 및 OAuth 관련 라이브러리를 설치.

```
# FastAPI 및 필수 라이브러리 설치
pip install fastapi uvicorn sqlalchemy mysql-connector-python python-dotenv

# OAuth와 SSO를 위한 라이브러리 설치
pip install authlib httpx

# 비밀번호 해시화를 위한 라이브러리 설치
pip install passlib[bcrypt]
```

### 1.3. FastAPI 서버 실행

아래 명령어를 통해 FastAPI 서버를 실

```
uvicorn app.main:app --reload
```

# FastAPI API 명세서

## 1. 사용자 회원가입 (Signup)

- **URL**: `/signup`
- **Method**: `POST`
- **Headers**:
  - `Content-Type`: `application/json`
- **Request Body**:
  ```json
  {
    "email": "string", // 사용자 이메일
    "password": "string" // 사용자 비밀번호
  }
  ```

나머지 API 명세서 예시는 텍스트로 제공하겠습니다.

---

## 2. 사용자 로그인 (Get Access Token)

- **URL**: `/token`
- **Method**: `POST`
- **Headers**:
  - `Content-Type`: `application/x-www-form-urlencoded`
- **Request Body** (`x-www-form-urlencoded`):
  - `username`: 사용자 이메일
  - `password`: 사용자 비밀번호
- **Response**:
  - **200 OK**: 로그인 성공 시 액세스 토큰 및 리프레시 토큰 반환
    ```json
    {
      "access_token": "string", // 액세스 토큰
      "refresh_token": "string", // 리프레시 토큰
      "token_type": "bearer" // 토큰 타입
    }
    ```
  - **400 Bad Request**: 이메일 또는 비밀번호가 잘못된 경우
    ```json
    {
      "detail": "Incorrect username or password"
    }
    ```

---

## 3. 사용자 정보 가져오기 (Get User Info)

- **URL**: `/users/me`
- **Method**: `GET`
- **Headers**:
  - `Authorization`: `Bearer <access_token>`
- **Response**:
  - **200 OK**:
    ```json
    {
      "id": 1, // 사용자 ID
      "email": "string", // 사용자 이메일
      "is_active": true // 활성화 상태
    }
    ```
  - **401 Unauthorized**: 토큰이 잘못되었거나 유효하지 않은 경우
    ```json
    {
      "detail": "Could not validate credentials"
    }
    ```
  - **404 Not Found**: 사용자가 존재하지 않을 때
    ```json
    {
      "detail": "User not found"
    }
    ```

---

## 4. SSO 로그인 요청 (SSO Login)

- **URL**: `/auth/{provider}/login`
- **Method**: `GET`
- **Path Parameters**:
  - `provider`: SSO 제공자 이름 (예: `google`, `kakao`, `apple`)
- **Response**:
  - **307 Temporary Redirect**: SSO 제공자의 로그인 페이지로 리디렉션
  - **400 Bad Request**: 지원하지 않는 SSO 제공자인 경우
    ```json
    {
      "detail": "Unsupported provider"
    }
    ```

---

## 5. SSO 인증 후 콜백 (SSO Callback)

- **URL**: `/auth/{provider}/callback`
- **Method**: `GET`
- **Path Parameters**:
  - `provider`: SSO 제공자 이름 (예: `google`, `kakao`, `apple`)
- **Response**:
  - **200 OK**: SSO 로그인 성공 시 액세스 토큰 및 사용자 정보 반환
    ```json
    {
      "access_token": "string", // 액세스 토큰
      "refresh_token": "string", // 리프레시 토큰
      "token_type": "bearer",
      "user_info": {
        "email": "string", // 사용자 이메일
        "provider": "string", // SSO 제공자 이름
        "provider_id": "string", // SSO 제공자의 사용자 고유 ID
        "is_active": true // 사용자 활성화 상태
      }
    }
    ```
  - **400 Bad Request**: SSO 인증 실패 시
    ```json
    {
      "detail": "Failed to authenticate: <에러 메시지>"
    }
    ```
  - **400 Bad Request**: SSO 제공자로부터 `email` 또는 `provider_id` 정보가 제공되지 않는 경우
    ```json
    {
      "detail": "Email or provider ID not provided by SSO provider"
    }
    ```
  - **400 Bad Request**: 지원하지 않는 SSO 제공자인 경우
    ```json
    {
      "detail": "Unsupported provider"
    }
    ```

---

## 6. 기본 라우트 (Root)

- **URL**: `/`
- **Method**: `GET`
- **Response**:
  - **200 OK**:
    ```json
    {
      "message": "SSO with FastAPI"
    }
    ```

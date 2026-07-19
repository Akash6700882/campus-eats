import uuid

from fastapi import APIRouter, HTTPException, Request, status

from app.core.deps import AuthSvc, CurrentUser, DbSession
from app.core.jwt import (
    InvalidTokenError,
    TokenType,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.core.rate_limit import limiter
from app.models.user import User
from app.schemas.auth import (
    ForgotPasswordRequest,
    LoginRequest,
    OtpRequestSchema,
    OtpVerifySchema,
    RefreshTokenRequest,
    ResetPasswordRequest,
    SignupRequest,
    TokenResponse,
    UserResponse,
)
from app.services.auth_service import AuthError

router = APIRouter(prefix="/auth", tags=["auth"])


def _tokens_for(user: User) -> TokenResponse:
    return TokenResponse(
        access_token=create_access_token(user.id, user.role.name),
        refresh_token=create_refresh_token(user.id, user.role.name),
    )


def _user_response(user: User) -> UserResponse:
    return UserResponse(
        id=user.id, full_name=user.full_name, email=user.email, phone=user.phone,
        role=user.role.name, is_verified=user.is_verified,
    )


@router.post("/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("10/minute")
async def signup(request: Request, payload: SignupRequest, db: DbSession, auth_service: AuthSvc) -> TokenResponse:
    try:
        user = await auth_service.signup(payload.full_name, payload.email, payload.phone, payload.password)
        await db.commit()
    except AuthError as exc:
        await db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, str(exc)) from exc
    return _tokens_for(user)


@router.post("/login", response_model=TokenResponse)
@limiter.limit("10/minute")
async def login(request: Request, payload: LoginRequest, auth_service: AuthSvc) -> TokenResponse:
    try:
        user = await auth_service.login(payload.email, payload.password)
    except AuthError as exc:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, str(exc)) from exc
    return _tokens_for(user)


@router.post("/otp/request", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("5/minute")
async def request_otp(request: Request, payload: OtpRequestSchema, auth_service: AuthSvc) -> None:
    await auth_service.request_otp(payload.phone)


@router.post("/otp/verify", response_model=TokenResponse)
@limiter.limit("10/minute")
async def verify_otp(request: Request, payload: OtpVerifySchema, auth_service: AuthSvc) -> TokenResponse:
    try:
        user = await auth_service.verify_otp_login(payload.phone, payload.otp_code)
    except AuthError as exc:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, str(exc)) from exc
    return _tokens_for(user)


@router.post("/forgot-password", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("5/minute")
async def forgot_password(request: Request, payload: ForgotPasswordRequest, auth_service: AuthSvc) -> None:
    await auth_service.forgot_password(payload.email)


@router.post("/reset-password", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("10/minute")
async def reset_password(
    request: Request, payload: ResetPasswordRequest, db: DbSession, auth_service: AuthSvc
) -> None:
    try:
        await auth_service.reset_password(payload.token, payload.new_password)
        await db.commit()
    except AuthError as exc:
        await db.rollback()
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(exc)) from exc


@router.post("/refresh", response_model=TokenResponse)
@limiter.limit("20/minute")
async def refresh(request: Request, payload: RefreshTokenRequest, auth_service: AuthSvc) -> TokenResponse:
    try:
        token_payload = decode_token(payload.refresh_token, TokenType.REFRESH)
        user = await auth_service.get_user_for_refresh(uuid.UUID(token_payload["sub"]))
    except (InvalidTokenError, AuthError) as exc:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid or expired refresh token") from exc
    return _tokens_for(user)


@router.get("/me", response_model=UserResponse)
async def me(current_user: CurrentUser) -> UserResponse:
    return _user_response(current_user)

import uuid
from datetime import datetime, timedelta, timezone
from enum import StrEnum

from jose import JWTError, jwt

from app.core.config import get_settings

settings = get_settings()


class TokenType(StrEnum):
    ACCESS = "access"
    REFRESH = "refresh"
    RESET = "reset"


class InvalidTokenError(Exception):
    pass


def _create_token(subject: str, role: str, token_type: TokenType, expires_delta: timedelta) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": subject,
        "role": role,
        "type": token_type.value,
        "iat": now,
        "exp": now + expires_delta,
        "jti": str(uuid.uuid4()),
    }
    return jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)


def create_access_token(user_id: uuid.UUID, role: str) -> str:
    return _create_token(
        str(user_id), role, TokenType.ACCESS, timedelta(minutes=settings.access_token_expire_minutes)
    )


def create_refresh_token(user_id: uuid.UUID, role: str) -> str:
    return _create_token(
        str(user_id), role, TokenType.REFRESH, timedelta(days=settings.refresh_token_expire_days)
    )


def create_reset_token(user_id: uuid.UUID, role: str) -> str:
    return _create_token(str(user_id), role, TokenType.RESET, timedelta(minutes=15))


def decode_token(token: str, expected_type: TokenType) -> dict:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])
    except JWTError as exc:
        raise InvalidTokenError(str(exc)) from exc

    if payload.get("type") != expected_type.value:
        raise InvalidTokenError(f"expected {expected_type.value} token, got {payload.get('type')}")

    return payload

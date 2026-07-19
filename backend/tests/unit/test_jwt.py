import uuid

import pytest

from app.core.jwt import (
    InvalidTokenError,
    TokenType,
    create_access_token,
    create_refresh_token,
    decode_token,
)

USER_ID = uuid.uuid4()


def test_access_token_round_trip():
    token = create_access_token(USER_ID, "customer")
    payload = decode_token(token, TokenType.ACCESS)
    assert payload["sub"] == str(USER_ID)
    assert payload["role"] == "customer"


def test_refresh_token_rejected_as_access_token():
    token = create_refresh_token(USER_ID, "customer")
    with pytest.raises(InvalidTokenError):
        decode_token(token, TokenType.ACCESS)


def test_garbage_token_rejected():
    with pytest.raises(InvalidTokenError):
        decode_token("not-a-jwt", TokenType.ACCESS)

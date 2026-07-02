from datetime import UTC, datetime, timedelta
from typing import Literal

import jwt
from pydantic import BaseModel


TokenType = Literal["access", "refresh"]


class TokenPayload(BaseModel):
    sub: str
    token_type: TokenType
    exp: int


class AuthTokenError(Exception):
    pass


def create_token(
    *,
    user_id: str,
    token_type: TokenType,
    secret_key: str,
    algorithm: str,
    expires_delta: timedelta,
) -> str:
    expires_at = datetime.now(UTC) + expires_delta

    payload = {
        "sub": user_id,
        "token_type": token_type,
        "exp": int(expires_at.timestamp()),
    }

    return jwt.encode(payload, secret_key, algorithm=algorithm)


def decode_token(
    *,
    token: str,
    expected_token_type: TokenType,
    secret_key: str,
    algorithm: str,
) -> TokenPayload:
    try:
        raw_payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        payload = TokenPayload.model_validate(raw_payload)
    except Exception as exc:
        raise AuthTokenError("Invalid token") from exc

    if payload.token_type != expected_token_type:
        raise AuthTokenError("Invalid token type")

    return payload
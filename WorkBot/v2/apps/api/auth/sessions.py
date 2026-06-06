from __future__ import annotations

import os
from typing import Any

from itsdangerous import BadSignature, URLSafeSerializer


SESSION_COOKIE_NAME = "workbot_session"


def _serializer() -> URLSafeSerializer:
    secret = os.environ.get("WORKBOT_SESSION_SECRET")

    if not secret:
        raise RuntimeError("WORKBOT_SESSION_SECRET is not configured.")

    return URLSafeSerializer(secret_key=secret, salt="workbot-session")


def create_session_token(*, user_id: str) -> str:
    return _serializer().dumps({"user_id": user_id})


def read_session_token(token: str) -> dict[str, Any] | None:
    try:
        payload = _serializer().loads(token)
    except BadSignature:
        return None

    if not isinstance(payload, dict):
        return None

    return payload
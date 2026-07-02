from __future__ import annotations

from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):

    database_url: str = "sqlite:///data/workbot.db"
    database_echo: bool = False

    auth_secret_key: str           = "change-me-in-dev"
    auth_jwt_algorithm: str        = "HS256"
    auth_access_token_minutes: int = 15
    auth_refresh_token_days: int   = 7
    auth_refresh_cookie_name: str  = "workbot_refresh_token"
    auth_cookie_secure: bool       = False
    
    auth_cookie_samesite: Literal["lax", "strict", "none"] = "lax"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="WORKBOT_",
        extra="ignore",
    )


settings = Settings()
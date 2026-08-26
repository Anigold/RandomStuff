# backend/app/cli/config.py

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CliConfig:
    api_base_url: str
    api_timeout_seconds: float = 10.0

    @classmethod
    def from_env(cls) -> "CliConfig":
        return cls(
            api_base_url=os.getenv(
                "WORKBOT_API_URL",
                "http://127.0.0.1:8000",
            ).rstrip("/"),
            api_timeout_seconds=float(
                os.getenv("WORKBOT_API_TIMEOUT", "10")
            ),
        )
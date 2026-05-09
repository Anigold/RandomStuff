from __future__ import annotations

import uvicorn
from fastapi import FastAPI

from apps.api.routes import health


def create_app() -> FastAPI:
    app = FastAPI(title="WorkBot API", version="0.1.0")
    app.include_router(health.router)
    return app


app = create_app()


def main() -> None:
    uvicorn.run("apps.api.main:app", host="127.0.0.1", port=8000, reload=True)


if __name__ == "__main__":
    main()

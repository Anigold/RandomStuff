from __future__ import annotations

import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from apps.api.routes import health, items, orders, stores, vendors


def create_app() -> FastAPI:
    app = FastAPI(title="WorkBot API", version="0.1.0")

    app.include_router(health.router)
    app.include_router(orders.router, prefix="/api")
    app.include_router(items.router, prefix="/api")
    app.include_router(stores.router, prefix="/api")
    app.include_router(vendors.router, prefix="/api")

    app.mount("/static", StaticFiles(directory="apps/api/static"), name="static")

    return app


app = create_app()


def main() -> None:
    uvicorn.run(
        "apps.api.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )


if __name__ == "__main__":
    main()
from __future__ import annotations

from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi import Depends
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from apps.api.routes import auth, health, items, orders, stores, vendors, me
from apps.api.auth.dependencies import get_current_user
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parents[2]
STATIC_DIR = BASE_DIR / "apps" / "web" / "static"

def create_app() -> FastAPI:
    app = FastAPI(title="WorkBot API", version="0.1.0")

    app.include_router(auth.router)
    app.include_router(me.router, prefix="/api")
    app.include_router(health.router)
    app.include_router(orders.router, prefix="/api")
    app.include_router(items.router, prefix="/api")
    app.include_router(stores.router, prefix="/api")
    app.include_router(vendors.router, prefix="/api")

    # app.mount("/admin", StaticFiles(directory="apps/web/static", html=True), name="admin")


    app.mount(
        "/admin/assets",
        StaticFiles(directory=STATIC_DIR),
        name="admin-assets",
    )


    @app.get("/admin")
    def admin_page(user=Depends(get_current_user)):
        return FileResponse(STATIC_DIR / "index.html")


    @app.get("/admin/")
    def admin_page_slash():
        return RedirectResponse(url="/admin")


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
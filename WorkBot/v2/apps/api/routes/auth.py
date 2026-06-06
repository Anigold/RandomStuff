from __future__ import annotations

from fastapi import APIRouter, Depends, Form, HTTPException, Response, status
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from starlette import status

from apps.api.auth.passwords import verify_password
from apps.api.auth.sessions import SESSION_COOKIE_NAME, create_session_token
from apps.api.dependencies import get_db_session
from workbot_core.infrastructure.database.repositories.user_repository import (
    SqlUserRepository,
)


router = APIRouter(tags=["auth"])


@router.get("/login", response_class=HTMLResponse)
def login_page() -> str:
    return """
    <!doctype html>
    <html lang="en">
    <head>
        <meta charset="utf-8">
        <title>WorkBot Login</title>
        <style>
            body {
                margin: 0;
                min-height: 100vh;
                display: grid;
                place-items: center;
                font-family: Arial, sans-serif;
                background: #f6f3fb;
                color: #2b2433;
            }

            form {
                display: grid;
                gap: 0.75rem;
                width: min(360px, calc(100vw - 2rem));
                padding: 1.5rem;
                background: white;
                border: 1px solid #ddd2ea;
                border-radius: 14px;
                box-shadow: 0 18px 50px rgb(55 42 78 / 18%);
            }

            input, button {
                padding: 0.65rem;
                font: inherit;
            }

            button {
                cursor: pointer;
                background: #6d5a8d;
                color: white;
                border: 0;
                border-radius: 8px;
            }
        </style>
    </head>
    <body>
        <form method="post" action="/login">
            <h1>WorkBot Login</h1>
            <input name="username" placeholder="Username" required>
            <input name="password" placeholder="Password" type="password" required>
            <button type="submit">Log in</button>
        </form>
    </body>
    </html>
    """


@router.post("/login")
def login(
    username: str = Form(...),
    password: str = Form(...),
    session: Session = Depends(get_db_session),
):
    user = SqlUserRepository(session).get_by_username(username)

    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password.",
        )

    if not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password.",
        )

    response = RedirectResponse(url="/admin", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=create_session_token(user_id=user.id),
        httponly=True,
        samesite="lax",
        secure=False,  # Set True when deployed behind HTTPS.
    )

    return response


@router.post("/logout")
def logout():
    response = RedirectResponse(
        url="/login",
        status_code=status.HTTP_303_SEE_OTHER,
    )

    response.delete_cookie(
        key=SESSION_COOKIE_NAME,
        path="/",
    )

    return response
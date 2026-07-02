from pydantic import BaseModel, Field


class LoginRequestSchema(BaseModel):
    username: str = Field(min_length=1)
    password: str = Field(min_length=1)


class CurrentUserSchema(BaseModel):
    id: str
    username: str
    email: str | None = None
    display_name: str | None = None


class AuthTokenResponseSchema(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: CurrentUserSchema


class LogoutResponseSchema(BaseModel):
    ok: bool = True
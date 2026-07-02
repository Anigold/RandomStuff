from fastapi import APIRouter, Depends

from apps.api.auth.dependencies import get_current_user
from apps.api.schemas.auth_schema import CurrentUserSchema
from workbot_core.domain.models.user import User


router = APIRouter(prefix="/api", tags=["me"])


def user_to_schema(user: User) -> CurrentUserSchema:
    return CurrentUserSchema(
        id=user.id,
        username=user.username,
        email=getattr(user, "email", None),
        display_name=getattr(user, "display_name", None),
    )


@router.get("/me", response_model=CurrentUserSchema)
def me(
    current_user: User = Depends(get_current_user),
) -> CurrentUserSchema:
    return user_to_schema(current_user)
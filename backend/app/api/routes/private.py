from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel

from app.api.deps import SessionDep
from app.models import (
    UserCreate,
    UserPublic,
)
from app.services import user as user_service

router = APIRouter(tags=["private"], prefix="/private")


class PrivateUserCreate(BaseModel):
    """Schema for creating users via private API.

    Attributes:
        email: User's email address.
        password: User's password.
        full_name: User's full name.
        is_verified: Whether the user is verified (unused currently).
    """

    email: str
    password: str
    full_name: str
    is_verified: bool = False


@router.post("/users/", response_model=UserPublic)
def create_user(user_in: PrivateUserCreate, session: SessionDep) -> Any:
    """Create a new user via private API.

    This endpoint is intended for internal service-to-service calls
    and does not require authentication.

    Args:
        user_in: The user data to create.
        session: Database session dependency.

    Returns:
        The newly created user.
    """
    user_create = UserCreate(
        email=user_in.email,
        password=user_in.password,
        full_name=user_in.full_name,
    )
    user = user_service.create_user(session=session, user_create=user_create)
    return user

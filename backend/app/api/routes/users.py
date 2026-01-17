import uuid
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi_refine import (
    FilterConfig,
    FilterField,
    RefineQuery,
    RefineResponse,
    SortConfig,
)

from app.api.deps.common import (
    CurrentUser,
    SessionDep,
    get_current_active_superuser,
)
from app.api.deps.refine import refine_query_dep
from app.core.config import settings
from app.core.security import verify_password
from app.models import (
    Message,
    UpdatePassword,
    User,
    UserCreate,
    UserPublic,
    UserRegister,
    UserUpdate,
    UserUpdateMe,
)
from app.services import user as user_service
from app.utils import generate_new_account_email, send_email

router = APIRouter(prefix="/users", tags=["users"])
owners_router = APIRouter(prefix="/owners", tags=["users"])

# Get table columns for Refine config (SQLModel provides __table__ at runtime)
_user_c = User.__table__.c  # type: ignore[attr-defined]

# Configure Refine query parameters for users
user_filter_config = FilterConfig(
    fields={
        "id": FilterField(column=_user_c.id, cast=uuid.UUID),
        "email": FilterField(column=_user_c.email, cast=str),
        "full_name": FilterField(column=_user_c.full_name, cast=str),
        "is_active": FilterField(column=_user_c.is_active, cast=bool),
        "is_superuser": FilterField(column=_user_c.is_superuser, cast=bool),
    },
    search_fields=[_user_c.email, _user_c.full_name],
)

user_sort_config = SortConfig(
    fields={
        "email": _user_c.email,
        "full_name": _user_c.full_name,
        "id": _user_c.id,
    }
)

UserQuery = Annotated[
    RefineQuery,
    refine_query_dep(User, user_filter_config, user_sort_config),
]


@router.get(
    "/",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=list[UserPublic],
)
@owners_router.get(
    "/",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=list[UserPublic],
)
def read_users(
    response: Response,
    session: SessionDep,
    query: UserQuery,
) -> Any:
    """Retrieve a paginated list of all users.

    Requires superuser privileges.
    Supports Refine's simple-rest pagination, sorting, and filtering.

    Args:
        response: FastAPI response object for setting headers.
        session: Database session dependency.
        query: Refine query parameters (pagination, sort, filter).

    Returns:
        List of users with x-total-count header.
    """
    users, count = user_service.get_users_paginated(
        session=session,
        skip=query.offset,
        limit=query.limit,
        conditions=query.conditions,
        order_by=query.order_by,
    )
    RefineResponse(response).set_total_count(count)
    return users


@router.post(
    "/", dependencies=[Depends(get_current_active_superuser)], response_model=UserPublic
)
def create_user(*, session: SessionDep, user_in: UserCreate) -> Any:
    """Create a new user.

    Requires superuser privileges. Sends welcome email if enabled.

    Args:
        session: Database session dependency.
        user_in: The user data to create.

    Returns:
        The newly created user.

    Raises:
        HTTPException: 400 if email already exists.
    """
    user = user_service.get_user_by_email(session=session, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )

    user = user_service.create_user(session=session, user_create=user_in)
    if settings.emails_enabled and user_in.email:
        email_data = generate_new_account_email(
            email_to=user_in.email, username=user_in.email, password=user_in.password
        )
        send_email(
            email_to=user_in.email,
            subject=email_data.subject,
            html_content=email_data.html_content,
        )
    return user


@router.patch("/me", response_model=UserPublic)
def update_user_me(
    *, session: SessionDep, user_in: UserUpdateMe, current_user: CurrentUser
) -> Any:
    """Update the current user's own profile.

    Allows updating non-admin fields like full_name and email.

    Args:
        session: Database session dependency.
        user_in: The profile data to update.
        current_user: The authenticated user to update.

    Returns:
        The updated user profile.

    Raises:
        HTTPException: 409 if new email already exists for another user.
    """
    if user_in.email:
        existing_user = user_service.get_user_by_email(
            session=session, email=user_in.email
        )
        if existing_user and existing_user.id != current_user.id:
            raise HTTPException(
                status_code=409, detail="User with this email already exists"
            )
    user = user_service.update_user_me(
        session=session, db_user=current_user, user_in=user_in
    )
    return user


@router.patch("/me/password", response_model=Message)
def update_password_me(
    *, session: SessionDep, body: UpdatePassword, current_user: CurrentUser
) -> Any:
    """Update the current user's password.

    Requires the current password for verification.

    Args:
        session: Database session dependency.
        body: Contains current and new password.
        current_user: The authenticated user.

    Returns:
        Success message confirming password update.

    Raises:
        HTTPException: 400 if current password incorrect or same as new.
    """
    if not verify_password(body.current_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect password")
    if body.current_password == body.new_password:
        raise HTTPException(
            status_code=400, detail="New password cannot be the same as the current one"
        )
    user_service.update_password(
        session=session, db_user=current_user, new_password=body.new_password
    )
    return Message(message="Password updated successfully")


@router.get("/me", response_model=UserPublic)
def read_user_me(current_user: CurrentUser) -> Any:
    """Retrieve the current authenticated user's profile.

    Args:
        current_user: The authenticated user.

    Returns:
        The current user's profile data.
    """
    return current_user


@router.delete("/me", response_model=Message)
def delete_user_me(session: SessionDep, current_user: CurrentUser) -> Any:
    """Delete the current user's own account.

    Superusers cannot delete themselves via this endpoint.

    Args:
        session: Database session dependency.
        current_user: The authenticated user to delete.

    Returns:
        Success message confirming deletion.

    Raises:
        HTTPException: 403 if user is a superuser.
    """
    if current_user.is_superuser:
        raise HTTPException(
            status_code=403, detail="Super users are not allowed to delete themselves"
        )
    user_service.delete_user(session=session, db_user=current_user)
    return Message(message="User deleted successfully")


@router.post("/signup", response_model=UserPublic)
def register_user(session: SessionDep, user_in: UserRegister) -> Any:
    """Register a new user account (public signup).

    Does not require authentication.

    Args:
        session: Database session dependency.
        user_in: The registration data.

    Returns:
        The newly created user.

    Raises:
        HTTPException: 400 if email already exists.
    """
    user = user_service.get_user_by_email(session=session, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system",
        )
    user_create = UserCreate.model_validate(user_in)
    user = user_service.create_user(session=session, user_create=user_create)
    return user


@router.get("/{user_id}", response_model=UserPublic)
@owners_router.get("/{user_id}", response_model=UserPublic)
def read_user_by_id(
    user_id: uuid.UUID, session: SessionDep, current_user: CurrentUser
) -> Any:
    """Retrieve a user by their ID.

    Regular users can only retrieve their own profile.
    Superusers can retrieve any user.

    Args:
        user_id: The UUID of the user to retrieve.
        session: Database session dependency.
        current_user: The authenticated user making the request.

    Returns:
        The requested user's profile.

    Raises:
        HTTPException: 403 if insufficient privileges.
    """
    user = user_service.get_user_by_id(session=session, user_id=user_id)
    if user == current_user:
        return user
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="The user doesn't have enough privileges",
        )
    return user


@router.patch(
    "/{user_id}",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=UserPublic,
)
def update_user(
    *,
    session: SessionDep,
    user_id: uuid.UUID,
    user_in: UserUpdate,
) -> Any:
    """Update a user by their ID.

    Requires superuser privileges. Can update admin-level fields.

    Args:
        session: Database session dependency.
        user_id: The UUID of the user to update.
        user_in: The updated user data.

    Returns:
        The updated user.

    Raises:
        HTTPException: 404 if user not found, 409 if email conflict.
    """
    db_user = user_service.get_user_by_id(session=session, user_id=user_id)
    if not db_user:
        raise HTTPException(
            status_code=404,
            detail="The user with this id does not exist in the system",
        )
    if user_in.email:
        existing_user = user_service.get_user_by_email(
            session=session, email=user_in.email
        )
        if existing_user and existing_user.id != user_id:
            raise HTTPException(
                status_code=409, detail="User with this email already exists"
            )

    db_user = user_service.update_user(
        session=session, db_user=db_user, user_in=user_in
    )
    return db_user


@router.delete("/{user_id}", dependencies=[Depends(get_current_active_superuser)])
def delete_user(
    session: SessionDep, current_user: CurrentUser, user_id: uuid.UUID
) -> Message:
    """Delete a user by their ID.

    Requires superuser privileges. Cannot delete yourself.

    Args:
        session: Database session dependency.
        current_user: The authenticated superuser.
        user_id: The UUID of the user to delete.

    Returns:
        Success message confirming deletion.

    Raises:
        HTTPException: 404 if user not found, 403 if trying to delete self.
    """
    user = user_service.get_user_by_id(session=session, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user == current_user:
        raise HTTPException(
            status_code=403, detail="Super users are not allowed to delete themselves"
        )
    user_service.delete_user_by_id(session=session, user_id=user_id)
    return Message(message="User deleted successfully")

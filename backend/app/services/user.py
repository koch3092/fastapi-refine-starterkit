import uuid
from typing import Any

from sqlalchemy import ColumnElement
from sqlmodel import Session, col, delete, func, select

from app.core.security import get_password_hash, verify_password
from app.models import Item, User, UserCreate, UserUpdate, UserUpdateMe


def create_user(*, session: Session, user_create: UserCreate) -> User:
    """Create a new user in the database.

    Args:
        session: Database session for the operation.
        user_create: User creation data including email and password.

    Returns:
        The newly created user entity with generated ID.
    """
    db_obj = User.model_validate(
        user_create, update={"hashed_password": get_password_hash(user_create.password)}
    )
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def update_user(*, session: Session, db_user: User, user_in: UserUpdate) -> Any:
    """Update an existing user with admin-level fields.

    Args:
        session: Database session for the operation.
        db_user: The existing user entity to update.
        user_in: Update data, may include password which will be hashed.

    Returns:
        The updated user entity.
    """
    user_data = user_in.model_dump(exclude_unset=True)
    extra_data = {}
    if "password" in user_data:
        password = user_data["password"]
        hashed_password = get_password_hash(password)
        extra_data["hashed_password"] = hashed_password
    db_user.sqlmodel_update(user_data, update=extra_data)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


def get_user_by_email(*, session: Session, email: str) -> User | None:
    """Retrieve a user by their email address.

    Args:
        session: Database session for the operation.
        email: The email address to search for.

    Returns:
        The user entity if found, None otherwise.
    """
    statement = select(User).where(User.email == email)
    session_user = session.exec(statement).first()
    return session_user


def authenticate(*, session: Session, email: str, password: str) -> User | None:
    """Authenticate a user by email and password.

    Args:
        session: Database session for the operation.
        email: The user's email address.
        password: The plain-text password to verify.

    Returns:
        The authenticated user entity if credentials are valid, None otherwise.
    """
    db_user = get_user_by_email(session=session, email=email)
    if not db_user:
        return None
    if not verify_password(password, db_user.hashed_password):
        return None
    return db_user


def get_users_paginated(
    *,
    session: Session,
    skip: int = 0,
    limit: int = 100,
    conditions: list[ColumnElement[Any]] | None = None,
    order_by: list[Any] | None = None,
) -> tuple[list[User], int]:
    """Retrieve a paginated list of users with total count.

    Args:
        session: Database session for the operation.
        skip: Number of records to skip for pagination.
        limit: Maximum number of records to return.
        conditions: Optional SQLAlchemy filter conditions from Refine query.
        order_by: Optional SQLAlchemy order_by clauses from Refine query.

    Returns:
        A tuple of (list of users, total count of all users).
    """
    # Count query
    count_statement = select(func.count()).select_from(User)
    if conditions:
        count_statement = count_statement.where(*conditions)
    count = session.exec(count_statement).one()

    # Data query
    statement = select(User)
    if conditions:
        statement = statement.where(*conditions)
    if order_by:
        statement = statement.order_by(*order_by)
    statement = statement.offset(skip).limit(limit)
    users = list(session.exec(statement).all())

    return users, count


def get_user_by_id(*, session: Session, user_id: uuid.UUID) -> User | None:
    """Retrieve a user by their unique identifier.

    Args:
        session: Database session for the operation.
        user_id: The UUID of the user to retrieve.

    Returns:
        The user entity if found, None otherwise.
    """
    return session.get(User, user_id)


def update_user_me(*, session: Session, db_user: User, user_in: UserUpdateMe) -> User:
    """Update a user's own profile with non-admin fields.

    Only allows updating fields that users can modify themselves,
    such as full_name and email.

    Args:
        session: Database session for the operation.
        db_user: The user entity to update.
        user_in: Update data with allowed self-update fields.

    Returns:
        The updated user entity.
    """
    user_data = user_in.model_dump(exclude_unset=True)
    db_user.sqlmodel_update(user_data)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


def update_password(*, session: Session, db_user: User, new_password: str) -> None:
    """Update a user's password.

    The password will be hashed before storage.

    Args:
        session: Database session for the operation.
        db_user: The user entity whose password to update.
        new_password: The new plain-text password to set.
    """
    hashed_password = get_password_hash(new_password)
    db_user.hashed_password = hashed_password
    session.add(db_user)
    session.commit()


def delete_user(*, session: Session, db_user: User) -> None:
    """Delete a user from the database.

    Associated items will be cascade deleted due to model relationship.

    Args:
        session: Database session for the operation.
        db_user: The user entity to delete.
    """
    session.delete(db_user)
    session.commit()


def delete_user_by_id(*, session: Session, user_id: uuid.UUID) -> None:
    """Delete a user by their ID, including all associated items.

    Explicitly deletes the user's items before deleting the user
    to ensure clean removal even without cascade.

    Args:
        session: Database session for the operation.
        user_id: The UUID of the user to delete.
    """
    statement = delete(Item).where(col(Item.owner_id) == user_id)
    session.exec(statement)  # type: ignore
    user = session.get(User, user_id)
    if user:
        session.delete(user)
        session.commit()

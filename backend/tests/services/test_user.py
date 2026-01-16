import uuid

from fastapi.encoders import jsonable_encoder
from sqlmodel import Session

from app.core.security import verify_password
from app.models import User, UserCreate, UserUpdate, UserUpdateMe
from app.services import item as item_service
from app.services import user as user_service
from tests.utils.item import create_random_item
from tests.utils.user import create_random_user
from tests.utils.utils import random_email, random_lower_string


def test_create_user(db: Session) -> None:
    """Test creating a new user.

    Verifies that user is created with correct email and has hashed password.
    """
    email = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=email, password=password)
    user = user_service.create_user(session=db, user_create=user_in)
    assert user.email == email
    assert hasattr(user, "hashed_password")


def test_authenticate_user(db: Session) -> None:
    """Test authenticating a user with valid credentials.

    Verifies that authenticate returns the correct user.
    """
    email = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=email, password=password)
    user = user_service.create_user(session=db, user_create=user_in)
    authenticated_user = user_service.authenticate(
        session=db, email=email, password=password
    )
    assert authenticated_user
    assert user.email == authenticated_user.email


def test_not_authenticate_user(db: Session) -> None:
    """Test authentication fails with non-existent user.

    Verifies that authenticate returns None for non-existent user.
    """
    email = random_email()
    password = random_lower_string()
    user = user_service.authenticate(session=db, email=email, password=password)
    assert user is None


def test_authenticate_user_wrong_password(db: Session) -> None:
    """Test authentication fails with wrong password.

    Verifies that authenticate returns None when password is incorrect.
    """
    email = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=email, password=password)
    user_service.create_user(session=db, user_create=user_in)
    authenticated_user = user_service.authenticate(
        session=db, email=email, password="wrongpassword1234"
    )
    assert authenticated_user is None


def test_check_if_user_is_active(db: Session) -> None:
    """Test that newly created user is active by default."""
    email = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=email, password=password)
    user = user_service.create_user(session=db, user_create=user_in)
    assert user.is_active is True


def test_check_if_user_is_active_inactive(db: Session) -> None:
    """Test creating an inactive user."""
    email = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=email, password=password, is_active=False)
    user = user_service.create_user(session=db, user_create=user_in)
    assert user.is_active is False


def test_check_if_user_is_superuser(db: Session) -> None:
    """Test creating a superuser."""
    email = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=email, password=password, is_superuser=True)
    user = user_service.create_user(session=db, user_create=user_in)
    assert user.is_superuser is True


def test_check_if_user_is_superuser_normal_user(db: Session) -> None:
    """Test that normal user is not a superuser by default."""
    username = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=username, password=password)
    user = user_service.create_user(session=db, user_create=user_in)
    assert user.is_superuser is False


def test_get_user_by_email(db: Session) -> None:
    """Test retrieving a user by email.

    Verifies that get_user_by_email returns the correct user.
    """
    email = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=email, password=password)
    created_user = user_service.create_user(session=db, user_create=user_in)
    fetched_user = user_service.get_user_by_email(session=db, email=email)
    assert fetched_user
    assert fetched_user.id == created_user.id
    assert fetched_user.email == email


def test_get_user_by_email_not_found(db: Session) -> None:
    """Test get_user_by_email returns None for non-existent email."""
    email = random_email()
    fetched_user = user_service.get_user_by_email(session=db, email=email)
    assert fetched_user is None


def test_get_user_by_id(db: Session) -> None:
    """Test retrieving a user by ID.

    Verifies that get_user_by_id returns the correct user.
    """
    user = create_random_user(db)
    fetched_user = user_service.get_user_by_id(session=db, user_id=user.id)
    assert fetched_user
    assert fetched_user.id == user.id
    assert fetched_user.email == user.email


def test_get_user_by_id_not_found(db: Session) -> None:
    """Test get_user_by_id returns None for non-existent ID."""
    non_existent_id = uuid.uuid4()
    fetched_user = user_service.get_user_by_id(session=db, user_id=non_existent_id)
    assert fetched_user is None


def test_get_user(db: Session) -> None:
    """Test getting user from database directly.

    Verifies user data consistency between service and direct DB access.
    """
    password = random_lower_string()
    username = random_email()
    user_in = UserCreate(email=username, password=password, is_superuser=True)
    user = user_service.create_user(session=db, user_create=user_in)
    user_2 = db.get(User, user.id)
    assert user_2
    assert user.email == user_2.email
    assert jsonable_encoder(user) == jsonable_encoder(user_2)


def test_update_user(db: Session) -> None:
    """Test updating a user with admin-level update.

    Verifies password update via update_user function.
    """
    password = random_lower_string()
    email = random_email()
    user_in = UserCreate(email=email, password=password, is_superuser=True)
    user = user_service.create_user(session=db, user_create=user_in)
    new_password = random_lower_string()
    user_in_update = UserUpdate(password=new_password, is_superuser=True)
    if user.id is not None:
        user_service.update_user(session=db, db_user=user, user_in=user_in_update)
    user_2 = db.get(User, user.id)
    assert user_2
    assert user.email == user_2.email
    assert verify_password(new_password, user_2.hashed_password)


def test_update_user_email(db: Session) -> None:
    """Test updating user email via update_user."""
    user = create_random_user(db)
    new_email = random_email()
    user_in_update = UserUpdate(email=new_email)
    updated_user = user_service.update_user(
        session=db, db_user=user, user_in=user_in_update
    )
    assert updated_user.email == new_email


def test_update_user_me(db: Session) -> None:
    """Test updating user's own profile.

    Verifies that update_user_me updates allowed fields.
    """
    user = create_random_user(db)
    new_full_name = "New Full Name"
    user_in_update = UserUpdateMe(full_name=new_full_name)
    updated_user = user_service.update_user_me(
        session=db, db_user=user, user_in=user_in_update
    )
    assert updated_user.full_name == new_full_name


def test_update_user_me_email(db: Session) -> None:
    """Test updating user's own email via update_user_me."""
    user = create_random_user(db)
    new_email = random_email()
    user_in_update = UserUpdateMe(email=new_email)
    updated_user = user_service.update_user_me(
        session=db, db_user=user, user_in=user_in_update
    )
    assert updated_user.email == new_email


def test_update_password(db: Session) -> None:
    """Test updating user password.

    Verifies that update_password correctly hashes and stores new password.
    """
    user = create_random_user(db)
    new_password = random_lower_string()
    user_service.update_password(session=db, db_user=user, new_password=new_password)
    # Refresh user from database
    db.refresh(user)
    assert verify_password(new_password, user.hashed_password)


def test_get_users_paginated(db: Session) -> None:
    """Test retrieving paginated list of users.

    Verifies pagination and count functionality.
    """
    # Create a few users
    for _ in range(3):
        create_random_user(db)

    users, count = user_service.get_users_paginated(session=db, skip=0, limit=100)
    assert count >= 3
    assert len(users) >= 3


def test_get_users_paginated_with_skip_limit(db: Session) -> None:
    """Test pagination with skip and limit parameters."""
    users_all, count = user_service.get_users_paginated(session=db, skip=0, limit=100)
    users_limited, _ = user_service.get_users_paginated(session=db, skip=0, limit=2)
    users_skipped, _ = user_service.get_users_paginated(session=db, skip=1, limit=2)

    assert len(users_limited) <= 2
    if len(users_all) > 1:
        assert users_skipped[0].id != users_limited[0].id


def test_delete_user(db: Session) -> None:
    """Test deleting a user.

    Verifies that delete_user removes user from database.
    """
    user = create_random_user(db)
    user_id = user.id
    user_service.delete_user(session=db, db_user=user)
    deleted_user = user_service.get_user_by_id(session=db, user_id=user_id)
    assert deleted_user is None


def test_delete_user_by_id(db: Session) -> None:
    """Test deleting a user by ID including associated items.

    Verifies that delete_user_by_id removes user and their items.
    """
    # Create a user with an item
    item = create_random_item(db)
    user_id = item.owner_id
    item_id = item.id

    # Delete the user
    user_service.delete_user_by_id(session=db, user_id=user_id)

    # Verify user is deleted
    deleted_user = user_service.get_user_by_id(session=db, user_id=user_id)
    assert deleted_user is None

    # Verify item is also deleted
    deleted_item = item_service.get_item_by_id(session=db, item_id=item_id)
    assert deleted_item is None

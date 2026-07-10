#!/usr/bin/env python3
"""Remove the starter kit's legacy demo Items resource."""

from __future__ import annotations

import argparse
import ast
import shutil
import subprocess
import uuid
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

PATHS_TO_REMOVE = [
    "backend/app/models/item.py",
    "backend/app/api/routes/items.py",
    "backend/app/services/item.py",
    "backend/tests/api/routes/test_items.py",
    "backend/tests/services/test_item.py",
    "backend/tests/utils/item.py",
    "frontend/src/pages/items",
]

MIGRATION_MESSAGE = "drop item table"
MIGRATION_SLUG = "drop_item_table"
MIGRATION_DOCSTRING = "Drop item table"
VERSIONS_DIR = ROOT / "backend/app/alembic/versions"

REPLACEMENTS: dict[str, list[tuple[str, str]]] = {
    "backend/app/models/__init__.py": [
        (
            """from app.models.item import (
    Item,
    ItemBase,
    ItemCreate,
    ItemPublic,
    ItemsPublic,
    ItemUpdate,
)
""",
            "",
        ),
        (
            '''    "Item",
    "ItemBase",
    "ItemCreate",
    "ItemPublic",
    "ItemsPublic",
    "ItemUpdate",
''',
            "",
        ),
    ],
    "backend/app/models/user.py": [
        (
            '    items: list["Item"] = Relationship(back_populates="owner", cascade_delete=True)\n',
            "",
        ),
        ("from app.models.item import Item\n", ""),
        ("    from app.models.item import Item\n", ""),
        (
            "if TYPE_CHECKING:\n    from app.models.asset import Asset\n    \n",
            "if TYPE_CHECKING:\n    from app.models.asset import Asset\n\n",
        ),
    ],
    "backend/app/models.py": [
        (
            '    items: list["Item"] = Relationship(back_populates="owner", cascade_delete=True)\n',
            "",
        ),
        ("# Shared properties\n# Shared asset properties\n", "# Shared asset properties\n"),
        (
            '''
# Shared properties
class ItemBase(SQLModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=255)


# Properties to receive on item creation
class ItemCreate(ItemBase):
    pass


# Properties to receive on item update
class ItemUpdate(ItemBase):
    title: str | None = Field(default=None, min_length=1, max_length=255)  # type: ignore


# Database model, database table inferred from class name
class Item(ItemBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    owner_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    owner: User | None = Relationship(back_populates="items")


# Properties to return via API, id is always required
class ItemPublic(ItemBase):
    id: uuid.UUID
    owner_id: uuid.UUID


class ItemsPublic(SQLModel):
    data: list[ItemPublic]
    count: int


''',
            "",
        ),
    ],
    "backend/app/api/main.py": [
        (
            "from app.api.routes import assets, items, login, private, users, utils\n",
            "from app.api.routes import assets, login, private, users, utils\n",
        ),
        ("api_router.include_router(items.router)\n", ""),
    ],
    "backend/app/services/user.py": [
        (
            "from sqlmodel import Session, col, delete, func, select\n",
            "from sqlmodel import Session, func, select\n",
        ),
        (
            "from app.models import Item, User, UserCreate, UserUpdate, UserUpdateMe\n",
            "from app.models import User, UserCreate, UserUpdate, UserUpdateMe\n",
        ),
        (
            """    Associated items will be cascade deleted due to model relationship.\n\n""",
            "",
        ),
        (
            '''def delete_user_by_id(*, session: Session, user_id: uuid.UUID) -> None:
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
''',
            '''def delete_user_by_id(*, session: Session, user_id: uuid.UUID) -> None:
    """Delete a user by their ID.

    Args:
        session: Database session for the operation.
        user_id: The UUID of the user to delete.
    """
    user = session.get(User, user_id)
    if user:
        session.delete(user)
        session.commit()
''',
        ),
    ],
    "backend/app/services/__init__.py": [
        (
            """from app.services.item import (
    create_item,
    delete_item,
    get_item_by_id,
    get_items_paginated,
    update_item,
)
""",
            "",
        ),
        (
            """    # Item services
    "create_item",
    "delete_item",
    "get_item_by_id",
    "get_items_paginated",
    "update_item",
""",
            "",
        ),
    ],
    "backend/tests/conftest.py": [
        (
            "from app.models import Asset, Item, User\n",
            "from app.models import Asset, User\n",
        ),
        (
            """        statement = delete(Item)
        session.execute(statement)
""",
            "",
        ),
    ],
    "backend/tests/services/test_user.py": [
        ("from app.services import item as item_service\n", ""),
        ("from tests.utils.item import create_random_item\n", ""),
        (
            '''def test_delete_user_by_id(db: Session) -> None:
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
''',
            '''def test_delete_user_by_id(db: Session) -> None:
    """Test deleting a user by ID."""
    user = create_random_user(db)
    user_id = user.id

    user_service.delete_user_by_id(session=db, user_id=user_id)

    deleted_user = user_service.get_user_by_id(session=db, user_id=user_id)
    assert deleted_user is None
''',
        ),
    ],
    "frontend/src/App.tsx": [
        (
            'import { Archive, Boxes, Users } from "lucide-react";\n',
            'import { Archive, Users } from "lucide-react";\n',
        ),
        (
            'import { ItemCreate, ItemEdit, ItemList, ItemShow } from "@/pages/items";\n',
            "",
        ),
        (
            '''          {
            name: "items",
            list: "/items",
            create: "/items/create",
            edit: "/items/edit/:id",
            show: "/items/show/:id",
            meta: {
              canDelete: true,
              icon: <Boxes />,
            },
          },
''',
            "",
        ),
        (
            '<Route index element={<NavigateToResource resource="items" />} />',
            '<Route index element={<NavigateToResource resource="assets" />} />',
        ),
        (
            '''            <Route path="/items">
              <Route index element={<ItemList />} />
              <Route path="create" element={<ItemCreate />} />
              <Route path="edit/:id" element={<ItemEdit />} />
              <Route path="show/:id" element={<ItemShow />} />
            </Route>
''',
            "",
        ),
    ],
    "frontend/src/components/refine-ui/layout/app-layout.tsx": [
        (
            'import { Archive, Boxes, FileText, LogOut, UserRound } from "lucide-react";\n',
            'import { Archive, FileText, LogOut, UserRound } from "lucide-react";\n',
        ),
        ("  items: <Boxes />,\n", ""),
        ("<Boxes className=\"size-4\" />", "<Archive className=\"size-4\" />"),
    ],
    "README.md": [
        (
            "The reusable infrastructure is intentionally small: JWT auth, users, items, S3-compatible\n",
            "The reusable infrastructure is intentionally small: JWT auth, users, S3-compatible\n",
        ),
        (
            "- **Users and items**: baseline CRUD resources for admin-console scaffolding\n",
            "- **Users**: baseline admin CRUD resource for admin-console scaffolding\n",
        ),
    ],
    "AGENTS.md": [
        (
            "- This repository is a business-agnostic starter kit. Keep auth, users, items, assets, Refine data access, migrations, tests, and docs reusable.\n",
            "- This repository is a business-agnostic starter kit. Keep auth, users, assets, Refine data access, migrations, tests, and docs reusable.\n",
        ),
    ],
}


def remove_path(relative_path: str) -> bool:
    path = ROOT / relative_path
    if path.is_dir():
        shutil.rmtree(path)
        return True
    if path.exists():
        path.unlink()
        return True
    return False


def apply_replacements(relative_path: str, replacements: list[tuple[str, str]]) -> bool:
    path = ROOT / relative_path
    if not path.exists():
        return False

    original = path.read_text()
    updated = original
    for old, new in replacements:
        updated = updated.replace(old, new)

    if updated == original:
        return False

    path.write_text(updated)
    return True


def has_drop_item_migration() -> bool:
    for path in VERSIONS_DIR.glob("*.py"):
        content = path.read_text()
        if f'"""{MIGRATION_DOCSTRING}' in content and 'op.drop_table("item")' in content:
            return True
    return False


def get_single_alembic_head() -> str:
    revisions: set[str] = set()
    down_revisions: set[str] = set()

    for path in VERSIONS_DIR.glob("*.py"):
        revision, dependencies = read_revision_metadata(path)
        if revision is None:
            continue
        revisions.add(revision)
        down_revisions.update(dependencies)

    heads = sorted(revisions - down_revisions)
    if len(heads) != 1:
        raise RuntimeError(
            "Expected exactly one Alembic head before removing Items. "
            "Resolve migration branches first, then rerun this script."
        )
    return heads[0]


def read_revision_metadata(path: Path) -> tuple[str | None, list[str]]:
    tree = ast.parse(path.read_text())
    revision: str | None = None
    down_revision: list[str] = []

    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        target_names = [
            target.id for target in node.targets if isinstance(target, ast.Name)
        ]
        if "revision" in target_names:
            revision = read_revision_value(node.value)
        if "down_revision" in target_names:
            down_revision = read_down_revision_value(node.value)

    return revision, down_revision


def read_revision_value(node: ast.AST) -> str | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None


def read_down_revision_value(node: ast.AST) -> list[str]:
    if isinstance(node, ast.Constant):
        if isinstance(node.value, str):
            return [node.value]
        return []
    if isinstance(node, ast.Tuple | ast.List):
        return [
            item.value
            for item in node.elts
            if isinstance(item, ast.Constant) and isinstance(item.value, str)
        ]
    return []


def render_migration(*, revision: str, down_revision: str) -> str:
    create_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
    return f'''"""{MIGRATION_DOCSTRING}

Revision ID: {revision}
Revises: {down_revision}
Create Date: {create_date}

"""

from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision = "{revision}"
down_revision = "{down_revision}"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_table("item")


def downgrade():
    op.create_table(
        "item",
        sa.Column(
            "description",
            sqlmodel.sql.sqltypes.AutoString(length=255),
            nullable=True,
        ),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "title",
            sqlmodel.sql.sqltypes.AutoString(length=255),
            nullable=False,
        ),
        sa.Column("owner_id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(["owner_id"], ["user.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
'''


def ensure_migration(down_revision: str | None) -> str | None:
    if has_drop_item_migration():
        return None

    if down_revision is None:
        down_revision = get_single_alembic_head()

    revision = uuid.uuid4().hex[:12]
    path = VERSIONS_DIR / f"{revision}_{MIGRATION_SLUG}.py"
    path.write_text(render_migration(revision=revision, down_revision=down_revision))
    return str(path.relative_to(ROOT))


def regenerate_client() -> None:
    subprocess.run(["bash", "scripts/generate-client.sh"], cwd=ROOT, check=True)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Remove the legacy demo Items resource from this starter kit."
    )
    parser.add_argument(
        "--skip-generate-client",
        action="store_true",
        help="Skip OpenAPI and frontend type regeneration.",
    )
    args = parser.parse_args()

    down_revision = None if has_drop_item_migration() else get_single_alembic_head()
    changed: list[str] = []

    for relative_path, replacements in REPLACEMENTS.items():
        if apply_replacements(relative_path, replacements):
            changed.append(relative_path)

    for relative_path in PATHS_TO_REMOVE:
        if remove_path(relative_path):
            changed.append(relative_path)

    migration_path = ensure_migration(down_revision)
    if migration_path:
        changed.append(migration_path)

    if not args.skip_generate_client:
        regenerate_client()

    if changed:
        print("Removed demo Items resource:")
        for relative_path in changed:
            print(f"- {relative_path}")
    else:
        print("Demo Items resource was already removed.")


if __name__ == "__main__":
    main()

import re
import unicodedata
import uuid
from pathlib import PurePosixPath

from app.storage.errors import S3ValidationError

_CONTROL_CHARS_RE = re.compile(r"[\x00-\x1f\x7f]")


def normalize_file_name(file_name: str) -> str:
    """Normalize a user-provided file name for safe object keys."""
    raw = file_name.strip()
    normalized_path = raw.replace("\\", "/")
    name = PurePosixPath(normalized_path).name.strip()

    if not name:
        raise S3ValidationError("file_name is required")

    name = unicodedata.normalize("NFC", name)
    name = _CONTROL_CHARS_RE.sub("_", name)

    if name in {".", ".."} or not name.strip():
        raise S3ValidationError("Invalid file_name")

    return name[:255]


def build_asset_object_key(
    *,
    owner_id: uuid.UUID,
    asset_id: uuid.UUID,
    file_name: str,
) -> str:
    """Build the final object key for a user-owned asset."""
    safe_file_name = normalize_file_name(file_name)
    return f"assets/{owner_id}/{asset_id}/{safe_file_name}"

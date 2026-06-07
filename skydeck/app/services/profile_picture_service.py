"""Validation helpers for encrypted user profile pictures."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path

from fastapi import UploadFile

from app.core.config import settings
from app.core.errors import PayloadTooLargeError, UnsupportedMediaError
from app.services.storage import secure_filename

_MAX_BYTES = settings.PROFILE_PICTURE_MAX_FILE_MB * 1024 * 1024
_IMAGE_TYPES = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".gif": "image/gif",
    ".webp": "image/webp",
}


@dataclass(frozen=True)
class ValidatedProfilePicture:
    """A safe profile picture payload ready for encryption."""

    filename: str
    mime_type: str
    size: int
    sha256: str
    contents: bytes


def read_and_validate_profile_picture(file: UploadFile) -> ValidatedProfilePicture:
    """Read and validate one profile picture upload."""
    contents = file.file.read()
    size = len(contents)

    if size == 0:
        raise UnsupportedMediaError("Profile picture cannot be empty")
    if size > _MAX_BYTES:
        raise PayloadTooLargeError(
            f"Profile picture exceeds {settings.PROFILE_PICTURE_MAX_FILE_MB} MB limit"
        )

    filename = secure_filename(file.filename or "profile-picture")
    mime_type = _detect_image_type(filename, contents)
    return ValidatedProfilePicture(
        filename=filename,
        mime_type=mime_type,
        size=size,
        sha256=hashlib.sha256(contents).hexdigest(),
        contents=contents,
    )


def _detect_image_type(filename: str, contents: bytes) -> str:
    """Return the trusted image MIME type after extension and content checks."""
    ext = Path(filename).suffix.lower()

    if ext in {".jpg", ".jpeg"} and contents.startswith(b"\xff\xd8\xff"):
        return _IMAGE_TYPES[ext]
    if ext == ".png" and contents.startswith(b"\x89PNG\r\n\x1a\n"):
        return _IMAGE_TYPES[ext]
    if ext == ".gif" and contents[:6] in {b"GIF87a", b"GIF89a"}:
        return _IMAGE_TYPES[ext]
    if ext == ".webp" and contents.startswith(b"RIFF") and contents[8:12] == b"WEBP":
        return _IMAGE_TYPES[ext]

    raise UnsupportedMediaError("Profile picture must be a valid JPG, PNG, GIF, or WebP image")

"""Validation and metadata helpers for message attachments."""

from __future__ import annotations

import hashlib
import io
import zipfile
from dataclasses import dataclass
from pathlib import Path

from fastapi import UploadFile

from app.core.config import settings
from app.core.errors import PayloadTooLargeError, UnsupportedMediaError
from app.services.storage import secure_filename

_MAX_FILE_BYTES = settings.MESSAGE_ATTACHMENT_MAX_FILE_MB * 1024 * 1024
_MAX_TOTAL_BYTES = settings.MESSAGE_ATTACHMENT_MAX_TOTAL_MB * 1024 * 1024
_MAX_FILES = settings.MESSAGE_ATTACHMENT_MAX_FILES

_IMAGE_TYPES = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".gif": "image/gif",
    ".webp": "image/webp",
}
_OFFICE_TYPES = {
    ".docx": ("application/vnd.openxmlformats-officedocument.wordprocessingml.document", "word/"),
    ".xlsx": ("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", "xl/"),
    ".pptx": ("application/vnd.openxmlformats-officedocument.presentationml.presentation", "ppt/"),
}
_TEXT_TYPES = {".txt", ".csv", ".log"}


@dataclass(frozen=True)
class ValidatedAttachment:
    """A safe attachment payload ready for encryption and storage."""

    filename: str
    mime_type: str
    size: int
    sha256: str
    contents: bytes


def read_and_validate_attachments(files: list[UploadFile] | None) -> list[ValidatedAttachment]:
    """Read uploaded files once and validate count, size, filename, and type."""
    if not files:
        return []
    if len(files) > _MAX_FILES:
        raise PayloadTooLargeError(f"Messages can include at most {_MAX_FILES} attachments")

    validated: list[ValidatedAttachment] = []
    total_size = 0
    for file in files:
        if not file.filename:
            continue

        contents = file.file.read()
        size = len(contents)
        total_size += size

        if size == 0:
            raise UnsupportedMediaError("Attachments cannot be empty")
        if size > _MAX_FILE_BYTES:
            raise PayloadTooLargeError(
                f"Attachment exceeds {settings.MESSAGE_ATTACHMENT_MAX_FILE_MB} MB limit"
            )
        if total_size > _MAX_TOTAL_BYTES:
            raise PayloadTooLargeError(
                f"Message attachments exceed {settings.MESSAGE_ATTACHMENT_MAX_TOTAL_MB} MB total"
            )

        filename = secure_filename(file.filename)
        mime_type = _detect_type(filename, contents)
        validated.append(
            ValidatedAttachment(
                filename=filename,
                mime_type=mime_type,
                size=size,
                sha256=hashlib.sha256(contents).hexdigest(),
                contents=contents,
            )
        )

    return validated


def _detect_type(filename: str, contents: bytes) -> str:
    """Return the trusted MIME type after extension and content checks."""
    ext = Path(filename).suffix.lower()

    if ext == ".pdf" and contents.startswith(b"%PDF-"):
        return "application/pdf"
    if ext in {".jpg", ".jpeg"} and contents.startswith(b"\xff\xd8\xff"):
        return _IMAGE_TYPES[ext]
    if ext == ".png" and contents.startswith(b"\x89PNG\r\n\x1a\n"):
        return _IMAGE_TYPES[ext]
    if ext == ".gif" and contents[:6] in {b"GIF87a", b"GIF89a"}:
        return _IMAGE_TYPES[ext]
    if ext == ".webp" and contents.startswith(b"RIFF") and contents[8:12] == b"WEBP":
        return _IMAGE_TYPES[ext]
    if ext in _TEXT_TYPES and _looks_like_text(contents):
        return "text/plain"
    if ext in _OFFICE_TYPES and _looks_like_openxml(contents, _OFFICE_TYPES[ext][1]):
        return _OFFICE_TYPES[ext][0]

    raise UnsupportedMediaError("Attachment type is not allowed or content does not match filename")


def _looks_like_text(contents: bytes) -> bool:
    try:
        text = contents.decode("utf-8")
    except UnicodeDecodeError:
        return False
    return "\x00" not in text


def _looks_like_openxml(contents: bytes, required_prefix: str) -> bool:
    if not contents.startswith(b"PK\x03\x04"):
        return False
    try:
        with zipfile.ZipFile(io.BytesIO(contents)) as archive:
            names = set(archive.namelist())
    except zipfile.BadZipFile:
        return False
    return "[Content_Types].xml" in names and any(
        name.startswith(required_prefix) for name in names
    )

"""Storage abstraction layer.

Provides a ``StorageProvider`` ABC so the application can swap between
local-disk and object-store (S3 / MinIO) backends without touching
business logic.
"""

from __future__ import annotations

import abc
import logging
import re
import unicodedata
from pathlib import Path

from app.core.config import settings
from app.core.errors import StorageError

logger = logging.getLogger(__name__)

_UNSAFE_CHARS = re.compile(r"[^\w\s\-.]", re.ASCII)


def secure_filename(name: str) -> str:
    """Sanitise a user-supplied filename against path-traversal attacks.

    Strips directory components, replaces non-ASCII, collapses whitespace,
    and removes anything that is not alphanumeric, dash, underscore, or dot.
    """
    name = unicodedata.normalize("NFKD", name)
    name = name.encode("ascii", "ignore").decode("ascii")
    for sep in ("/", "\\"):
        name = name.replace(sep, "_")
    name = _UNSAFE_CHARS.sub("", name).strip(". ")
    name = re.sub(r"\s+", "_", name)
    return name or "unnamed"


class StorageProvider(abc.ABC):
    """Abstract base for file persistence backends."""

    @abc.abstractmethod
    def save(self, relative_path: str, data: bytes) -> str:
        """Persist *data* and return the canonical path/key."""

    @abc.abstractmethod
    def read(self, path: str) -> bytes:
        """Return raw bytes for the given path/key."""

    @abc.abstractmethod
    def delete(self, path: str) -> None:
        """Remove the object. Must not raise if already absent."""

    @abc.abstractmethod
    def exists(self, path: str) -> bool:
        """Return True when the object is present."""


class LocalStorage(StorageProvider):
    """Persist files on the local filesystem under *base_dir*."""

    def __init__(self, base_dir: str) -> None:
        self._base = Path(base_dir)
        self._base.mkdir(parents=True, exist_ok=True)

    def _resolve(self, relative_path: str) -> Path:
        """Resolve a storage key while preventing escape from the base directory."""
        resolved = (self._base / relative_path).resolve()
        if not str(resolved).startswith(str(self._base.resolve())):
            raise StorageError("Path traversal detected")
        return resolved

    def save(self, relative_path: str, data: bytes) -> str:
        """Write bytes to disk, creating parent folders as needed."""
        target = self._resolve(relative_path)
        try:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
        except OSError as exc:
            logger.error("Disk write failed for %s: %s", target, exc)
            raise StorageError(f"Failed to write file to disk: {exc}") from exc
        return str(target)

    def read(self, path: str) -> bytes:
        """Read a stored file from disk."""
        target = Path(path)
        if not target.is_file():
            raise StorageError(f"File not found on disk: {path}")
        try:
            return target.read_bytes()
        except OSError as exc:
            logger.error("Disk read failed for %s: %s", target, exc)
            raise StorageError(f"Failed to read file: {exc}") from exc

    def delete(self, path: str) -> None:
        """Best-effort delete; missing files are treated as already deleted."""
        target = Path(path)
        try:
            if target.is_file():
                target.unlink()
        except OSError as exc:
            logger.warning("Failed to delete %s: %s", target, exc)

    def exists(self, path: str) -> bool:
        """Return whether a stored file exists on disk."""
        return Path(path).is_file()


def get_manual_storage() -> StorageProvider:
    """Return the configured storage provider for manuals."""
    return LocalStorage(settings.STORAGE_DIR)


def get_submission_storage() -> StorageProvider:
    """Return the configured storage provider for submission attachments."""
    return LocalStorage(settings.SUBMISSIONS_STORAGE_DIR)


def get_message_attachment_storage() -> StorageProvider:
    """Return the configured storage provider for encrypted message attachments."""
    return LocalStorage(settings.MESSAGE_ATTACHMENTS_STORAGE_DIR)


def get_profile_picture_storage() -> StorageProvider:
    """Return the configured storage provider for encrypted profile pictures."""
    return LocalStorage(settings.PROFILE_PICTURES_STORAGE_DIR)

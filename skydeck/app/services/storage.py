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
        resolved = (self._base / relative_path).resolve()
        if not str(resolved).startswith(str(self._base.resolve())):
            raise StorageError("Path traversal detected")
        return resolved

    def save(self, relative_path: str, data: bytes) -> str:
        target = self._resolve(relative_path)
        try:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
        except OSError as exc:
            logger.error("Disk write failed for %s: %s", target, exc)
            raise StorageError(f"Failed to write file to disk: {exc}") from exc
        return str(target)

    def read(self, path: str) -> bytes:
        target = Path(path)
        if not target.is_file():
            raise StorageError(f"File not found on disk: {path}")
        try:
            return target.read_bytes()
        except OSError as exc:
            logger.error("Disk read failed for %s: %s", target, exc)
            raise StorageError(f"Failed to read file: {exc}") from exc

    def delete(self, path: str) -> None:
        target = Path(path)
        try:
            if target.is_file():
                target.unlink()
        except OSError as exc:
            logger.warning("Failed to delete %s: %s", target, exc)

    def exists(self, path: str) -> bool:
        return Path(path).is_file()


def get_manual_storage() -> StorageProvider:
    return LocalStorage(settings.STORAGE_DIR)


def get_submission_storage() -> StorageProvider:
    return LocalStorage(settings.SUBMISSIONS_STORAGE_DIR)

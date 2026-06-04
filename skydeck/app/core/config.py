"""Application settings loaded from environment variables and .env."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Resolve from this file so settings work no matter where the process starts.
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
_ENV_FILE = _PROJECT_ROOT / ".env"


class Settings(BaseSettings):
    """Application configuration.

    Resolution order (highest → lowest):
        1. Process environment variables
        2. ``.env`` file (resolved relative to the project root,
           not the working directory — safe for ``uvicorn --reload``)
        3. Defaults below
    """

    model_config = SettingsConfigDict(
        env_file=str(_ENV_FILE),
        env_file_encoding="utf-8",
        env_ignore_empty=True,
        extra="ignore",
    )

    # ── application ────────────────────────────────────────
    APP_NAME: str = "SkyDeck"
    DEBUG: bool = False
    BACKEND_PORT: int = 8000

    # ── postgres (decomposed — used by Docker & compose) ───
    POSTGRES_USER: str = "skydeck"
    POSTGRES_PASSWORD: str = "skydeck"
    POSTGRES_DB: str = "skydeck"
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: int = 5432

    # Direct override — when present takes precedence over
    # the decomposed POSTGRES_* vars above.
    DATABASE_URL: Optional[str] = None

    # ── connection pool ────────────────────────────────────
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_POOL_RECYCLE: int = 300

    # ── security / jwt ─────────────────────────────────────
    SECRET_KEY: str = "CHANGE-ME-generate-a-64-byte-random-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ── file storage ────────────────────────────────────────
    STORAGE_DIR: str = "storage/manuals"
    SUBMISSIONS_STORAGE_DIR: str = "storage/submissions"
    WATERMARK_FONT_SIZE: int = 40
    MAX_UPLOAD_SIZE_MB: int = 50

    # ── cors ───────────────────────────────────────────────
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:5173"]

    # ── seed ───────────────────────────────────────────────
    RUN_SEED: bool = False

    @model_validator(mode="after")
    def assemble_database_url(self) -> Settings:
        """Build or normalise DATABASE_URL.

        If DATABASE_URL was not supplied, assemble it from the
        decomposed POSTGRES_* variables.

        If it *was* supplied but uses the bare ``postgresql://``
        scheme (which resolves to psycopg v3 in modern SQLAlchemy),
        rewrite it to ``postgresql+psycopg2://`` so we always use
        the driver that is actually installed.
        """
        if self.DATABASE_URL is None:
            self.DATABASE_URL = (
                f"postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
                f"@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
            )
        else:
            url = self.DATABASE_URL
            if url.startswith("postgresql://"):
                self.DATABASE_URL = "postgresql+psycopg2://" + url[len("postgresql://") :]
            elif url.startswith("postgres://"):
                self.DATABASE_URL = "postgresql+psycopg2://" + url[len("postgres://") :]
        return self


settings = Settings()

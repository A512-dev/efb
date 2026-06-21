"""Application exceptions and their standard HTTP error envelope.

Repositories and services can raise these errors without importing FastAPI
response classes. The single registered handler converts every ``AppError``
into ``{"error": "...", "code": 4XX/5XX}`` at the outer HTTP boundary.
"""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


class AppError(Exception):
    """Base application error that maps to a JSON error response."""

    def __init__(self, message: str, code: int = 400) -> None:
        """Store the client-safe message and HTTP status code."""
        # Keep explicit public fields because the response handler serializes
        # these values directly instead of exposing Exception internals.
        self.message = message
        self.code = code


class AuthenticationError(AppError):
    """Signal that no valid authenticated identity could be established."""

    def __init__(self, message: str = "Invalid credentials") -> None:
        """Create a 401 authentication failure."""
        super().__init__(message=message, code=401)


class AuthorisationError(AppError):
    """Signal that an authenticated user lacks permission for an action."""

    def __init__(self, message: str = "Not authorised") -> None:
        """Create a 403 permission failure."""
        super().__init__(message=message, code=403)


class NotFoundError(AppError):
    """Signal that a requested resource is absent or hidden from the caller."""

    def __init__(self, message: str = "Resource not found") -> None:
        """Create a 404 missing-or-hidden-resource failure."""
        super().__init__(message=message, code=404)


class ConflictError(AppError):
    """Signal that valid input conflicts with existing persistent state."""

    def __init__(self, message: str = "Resource already exists") -> None:
        """Create a 409 persistent-state conflict."""
        super().__init__(message=message, code=409)


class UnsupportedMediaError(AppError):
    """Signal that uploaded bytes are not an accepted file format."""

    def __init__(self, message: str = "Unsupported file type") -> None:
        """Create a 415 upload-format failure."""
        super().__init__(message=message, code=415)


class PayloadTooLargeError(AppError):
    """Signal that an upload exceeds a configured size limit."""

    def __init__(self, message: str = "File exceeds maximum allowed size") -> None:
        """Create a 413 configured-size-limit failure."""
        super().__init__(message=message, code=413)


class StorageError(AppError):
    """Raised when a disk/object-store write or read fails."""

    def __init__(self, message: str = "Storage operation failed") -> None:
        """Create a 500 storage read/write/integrity failure."""
        super().__init__(message=message, code=500)


class PDFProcessingError(AppError):
    """Raised when watermarking or PDF reading fails at runtime."""

    def __init__(self, message: str = "PDF processing failed") -> None:
        """Create a 500 PDF parsing or watermarking failure."""
        super().__init__(message=message, code=500)


def register_error_handlers(app: FastAPI) -> None:
    """Attach custom exception handlers to a FastAPI application instance."""

    @app.exception_handler(AppError)
    async def _app_error_handler(_request: Request, exc: AppError) -> JSONResponse:
        """Convert AppError exceptions into the API's standard JSON envelope."""
        return JSONResponse(
            status_code=exc.code,
            content={"error": exc.message, "code": exc.code},
        )

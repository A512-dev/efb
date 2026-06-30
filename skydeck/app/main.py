#skydeck\app\main.py
"""FastAPI application assembly and router registration.

This is the backend's composition root: it creates the application, installs
global error handling, and mounts each feature router. Running
``uvicorn app.main:app`` imports this module and exposes the ``app`` object.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from sqladmin import Admin
from starlette.middleware.sessions import SessionMiddleware

from app.admin.auth import AdminAuth
from app.admin.user_admin import UserAdmin
from app.api.v1.auth import router as auth_router
from app.api.v1.manual_categories import router as manual_categories_router
from app.api.v1.manual_reads import router as manual_reads_router
from app.api.v1.manual_updates import router as manual_updates_router
from app.api.v1.manuals import router as manuals_router
from app.api.v1.messages import router as messages_router
from app.api.v1.users import router as users_router
from app.core.config import settings
from app.core.errors import register_error_handlers
from app.db.session import engine


@asynccontextmanager
async def lifespan(application: FastAPI):
    """Verify database connectivity once at startup.

    FastAPI enters this context before accepting requests. A tiny ``SELECT 1``
    fails early with a useful configuration message instead of allowing the
    first real API request to discover a broken database connection.

    ``application`` is required by FastAPI's lifespan protocol even though
    this implementation does not need to mutate the application instance.
    """
    from sqlalchemy import text

    from app.db.session import engine

    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception as exc:
        raise RuntimeError(
            f"Database connection failed at startup.\n"
            f"  DATABASE_URL = {settings.DATABASE_URL}\n"
            f"  Error        = {exc}\n"
            f"Check your .env file and ensure PostgreSQL is running."
        ) from exc

    # Control returns to FastAPI while the server is alive. Code placed after
    # this yield would run during shutdown; there is currently no app-wide
    # resource to release because request sessions close themselves.
    yield


# Creating the object at import time is conventional for ASGI servers: Uvicorn
# imports ``app.main`` and looks up this module-level name.
app = FastAPI(
    title="SkyDeck API",
    description="Aviation Safety System MVP",
    version="1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)


app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SECRET_KEY,
    session_cookie="skydeck_admin",
    max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
    same_site="strict",
    https_only=not settings.DEBUG,
    path="/admin",
)



# Translate domain-level AppError exceptions into one consistent JSON shape.
register_error_handlers(app)

# All public API routes currently live under the versioned /api/v1 prefix.
app.include_router(auth_router, prefix="/api/v1")
app.include_router(users_router, prefix="/api/v1")
app.include_router(manuals_router, prefix="/api/v1")
app.include_router(manual_categories_router, prefix="/api/v1")
app.include_router(manual_reads_router, prefix="/api/v1")
app.include_router(manual_updates_router, prefix="/api/v1")
app.include_router(messages_router, prefix="/api/v1")


@app.get("/health", tags=["ops"])
def health_check() -> dict:
    """Lightweight liveness endpoint for deployments and smoke tests."""
    return {"status": "ok", "app": settings.APP_NAME}


admin_auth = AdminAuth(secret_key=settings.SECRET_KEY)

admin = Admin(
    app,
    engine,
    authentication_backend=admin_auth,
)
admin.add_view(UserAdmin)

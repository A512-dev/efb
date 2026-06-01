from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1.auth import router as auth_router
from app.api.v1.forms import router as forms_router
from app.api.v1.manual_updates import router as manual_updates_router
from app.api.v1.manuals import router as manuals_router
from app.api.v1.messages import router as messages_router
from app.api.v1.submissions import router as submissions_router
from app.api.v1.users import router as users_router
from app.core.config import settings
from app.core.errors import register_error_handlers


@asynccontextmanager
async def lifespan(application: FastAPI):
    """Verify database connectivity once at startup."""
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

    yield


app = FastAPI(
    title="SkyDeck API",
    description="Aviation Safety System MVP",
    version="1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

register_error_handlers(app)

app.include_router(auth_router, prefix="/api/v1")
app.include_router(users_router, prefix="/api/v1")
app.include_router(manuals_router, prefix="/api/v1")
app.include_router(manual_updates_router, prefix="/api/v1")
app.include_router(forms_router, prefix="/api/v1")
app.include_router(submissions_router, prefix="/api/v1")
app.include_router(messages_router, prefix="/api/v1")


@app.get("/health", tags=["ops"])
def health_check() -> dict:
    return {"status": "ok", "app": settings.APP_NAME}

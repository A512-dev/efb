"""Database engine and FastAPI session dependency.

The engine owns the process-wide connection pool. ``SessionLocal`` creates
lightweight units of work that borrow connections from that pool, while
``get_db`` adapts those sessions to FastAPI's dependency lifecycle.
"""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings

# Construct one engine per Python process. ``pool_pre_ping`` detects stale
# PostgreSQL connections before handing them to a request, and ``pool_recycle``
# periodically replaces long-lived connections.
engine = create_engine(
    settings.DATABASE_URL,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_pre_ping=True,
    pool_recycle=settings.DB_POOL_RECYCLE,
)

# Callers explicitly commit transactions. Disabling autoflush also means a
# query does not unexpectedly push pending changes unless code calls flush or
# commit itself.
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def get_db() -> Generator[Session, None, None]:
    """Yield one SQLAlchemy session per request and always close it.

    FastAPI advances the generator to obtain ``db``, injects that same object
    into the route and nested dependencies, then executes the ``finally`` block
    after the response is produced. Closing returns any borrowed connection to
    the engine pool; it does not dispose the process-wide engine.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

"""Connect Alembic's migration runner to the SkyDeck application.

Alembic imports this module for every migration command. The module performs
three pieces of wiring before choosing an execution mode:

1. load the same database URL used by the running application;
2. import every ORM model so it is registered in ``Base.metadata``;
3. expose that metadata to Alembic's autogeneration machinery.

No schema changes are defined here. Individual revisions under ``versions``
own the ordered ``upgrade`` and ``downgrade`` operations.
"""

from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from app.core.config import settings
from app.db.base import Base

# Importing the model package has a deliberate side effect: each model class
# registers its table with Base.metadata. Alembic needs the complete metadata
# graph to compare Python models with the current database schema.
import app.models  # noqa: F401

# ``context.config`` is Alembic's Config object, populated from alembic.ini and
# command-line options. It is available only while Alembic runs this module.
config = context.config

# Reuse Alembic's logging configuration when an .ini file was supplied.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Environment variables/.env are the source of truth for the connection URL.
# Overwriting the .ini value prevents migrations from silently targeting a
# different database than the API.
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# Autogenerate commands inspect this metadata to discover model-side changes.
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Render SQL without opening a live database connection.

    Offline mode is useful for ``alembic upgrade ... --sql``. Values are
    embedded literally so the generated script can be reviewed or executed by
    a database administrator later.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations against the configured database.

    Alembic creates a short-lived engine with ``NullPool`` because migration
    commands are one-off processes and do not benefit from the application's
    long-lived connection pool.
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


# Alembic decides the mode from CLI flags; both paths execute the same ordered
# revision chain, differing only in whether SQL is emitted or immediately run.
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

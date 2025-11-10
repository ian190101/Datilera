# alembic/env.py
from __future__ import annotations

import os
import sys
import asyncio
from pathlib import Path
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

# ---------------------------------------------------------------------
# Logging desde alembic.ini (handlers/levels)
# ---------------------------------------------------------------------
config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ---------------------------------------------------------------------
# Cargar .env (opcional pero útil en CLI) y ruta del proyecto
# ---------------------------------------------------------------------
try:
    from dotenv import load_dotenv  # type: ignore
    # No sobreescribir variables ya presentes en el entorno
    load_dotenv(override=False)
except Exception:
    pass

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# ---------------------------------------------------------------------
# Importar metadata de modelos
# ---------------------------------------------------------------------
from app.infrastructure.db.models import Base  # noqa: E402

target_metadata = Base.metadata

# ---------------------------------------------------------------------
# URL desde el entorno
# ---------------------------------------------------------------------
def get_url() -> str:
    url = os.getenv("DATABASE_URL", "").strip()
    if not url:
        raise RuntimeError("DATABASE_URL no está definida en el entorno")
    return url


# ---------------------------------------------------------------------
# Modo offline
# ---------------------------------------------------------------------
def run_migrations_offline() -> None:
    url = get_url()
    is_sqlite = url.startswith("sqlite")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
        render_as_batch=is_sqlite,  # útil para SQLite
    )
    with context.begin_transaction():
        context.run_migrations()


# ---------------------------------------------------------------------
# Modo online (async)
# ---------------------------------------------------------------------
def _do_run_migrations(connection: Connection, *, is_sqlite: bool) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
        render_as_batch=is_sqlite,
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    # Inyectar la URL en la config de Alembic para la plantilla async
    url = get_url()
    config.set_main_option("sqlalchemy.url", url)
    cfg_section = config.get_section(config.config_ini_section, {}) or {}
    connectable = async_engine_from_config(
        cfg_section, prefix="sqlalchemy.", poolclass=pool.NullPool
    )
    async with connectable.connect() as connection:
        await connection.run_sync(lambda conn: _do_run_migrations(conn, is_sqlite=url.startswith("sqlite")))
    await connectable.dispose()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

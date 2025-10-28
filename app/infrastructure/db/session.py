from __future__ import annotations

import os
import sys
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

# -----------------------------------------------------------------------------
# Configuración base
# -----------------------------------------------------------------------------
def _require_env(name: str) -> str:
    val = os.getenv(name)
    if not val:
        msg = f"{name} no está definido en el entorno (.env). Debes configurar la cadena de conexión asíncrona."
        raise RuntimeError(msg)
    return val

DATABASE_URL = _require_env("DATABASE_URL").strip()

# Validación simple del driver async
if not (
    DATABASE_URL.startswith("mysql+aiomysql://")
    or DATABASE_URL.startswith("postgresql+asyncpg://")
    or DATABASE_URL.startswith("sqlite+aiosqlite://")
):
    raise RuntimeError(
        "DATABASE_URL debe usar un driver asíncrono: "
        "MySQL: mysql+aiomysql:// | Postgres: postgresql+asyncpg:// | SQLite: sqlite+aiosqlite://"
    )

SQL_ECHO = os.getenv("SQL_ECHO", "0") == "1"
ISOLATION_LEVEL = os.getenv("SQL_ISOLATION", "").strip() or None  # p.ej. READ COMMITTED, REPEATABLE READ

# -----------------------------------------------------------------------------
# Pooling según driver
# -----------------------------------------------------------------------------
engine_kwargs: dict = {
    "echo": SQL_ECHO,
    "pool_pre_ping": True,   # reconexión segura
}

if ISOLATION_LEVEL:
    engine_kwargs["isolation_level"] = ISOLATION_LEVEL

if DATABASE_URL.startswith("sqlite+aiosqlite://"):
    # SQLite: sin pooling
    engine_kwargs["poolclass"] = NullPool
else:
    # MySQL/Postgres: pooling configurable
    engine_kwargs.update(
        pool_recycle=int(os.getenv("SQL_POOL_RECYCLE", "1800")),  # 30 min
        pool_size=int(os.getenv("SQL_POOL_SIZE", "10")),
        max_overflow=int(os.getenv("SQL_MAX_OVERFLOW", "20")),
    )

engine = create_async_engine(DATABASE_URL, **engine_kwargs)

# -----------------------------------------------------------------------------
# Session factory (una sesión por request/caso de uso)
# -----------------------------------------------------------------------------
AsyncSessionLocal: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
)

# -----------------------------------------------------------------------------
# Estrategia A (recomendada): transacción en capa superior
# Usa UnitOfWork o estos helpers; los repos NO llaman begin() internamente.
# -----------------------------------------------------------------------------
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependencia para FastAPI u otras capas: entrega una sesión.
    La transacción se controla arriba (UoW o session.begin()).
    """
    async with AsyncSessionLocal() as session:
        yield session

@asynccontextmanager
async def session_scope() -> AsyncGenerator[AsyncSession, None]:
    """
    Contexto con transacción por operación; no mezclar con begin() en repos.
    """
    async with AsyncSessionLocal() as session:
        async with session.begin():
            yield session

# -----------------------------------------------------------------------------
# Lifespan
# -----------------------------------------------------------------------------
async def dispose_engine() -> None:
    await engine.dispose()

def configure_sql_logging(level: int = logging.INFO) -> None:
    """
    Activa logging del SQL de forma estructurada sin usar echo en producción.
    """
    logger = logging.getLogger("sqlalchemy.engine")
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter("%(asctime)s %(levelname)s sqlalchemy %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    logger.setLevel(level)

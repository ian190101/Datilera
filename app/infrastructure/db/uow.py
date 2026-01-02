from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncGenerator, AsyncIterator, cast

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.infrastructure.db.repositories.acceso.codigos_acceso_repo import CodigosAccesoRepository  # <-- esto es nuevo
from app.infrastructure.db.repositories.alumnos.alumnos_repo import AlumnosRepository  # <-- esto es nuevo
from app.infrastructure.db.repositories.academico.grupos_repo import GruposRepository
from app.infrastructure.db.repositories.acceso.codigos_acceso_usos_repo import CodigosAccesoUsosRepository


class UnitOfWork:
    """
    Unit of Work para SQLAlchemy async.

    Reglas:
    - Crear SIEMPRE una instancia por request/caso de uso (no reutilizar entre corrutinas).
    - El UoW abre la transacción (repositorios no deben llamar begin()).
    - Provee session_required para asegurar uso dentro de una transacción.
    - Soporta begin_nested() con SAVEPOINT para secciones recuperables.
    """

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self._session_factory = session_factory
        self.session: AsyncSession | None = None
        self._ctx = None  # contexto interno para __aenter__/__aexit__

    # Uso directo: `async with UnitOfWork(factory) as uow: ...`
    async def __aenter__(self) -> "UnitOfWork":
        self._ctx = self.begin()
        return await self._ctx.__aenter__()

    async def __aexit__(self, exc_type, exc, tb) -> None:
        # delega en el contexto real
        if self._ctx is not None:
            await self._ctx.__aexit__(exc_type, exc, tb)  # type: ignore[attr-defined]
            self._ctx = None

    @asynccontextmanager
    async def begin(self) -> AsyncGenerator[UnitOfWork, None]:
        # 1. Re-entrancia: Si ya estamos dentro de un bloque 'async with uow', reutilizar.
        if self.session is not None:
            yield self
            return

        async with self._session_factory() as s:
            self.session = s
            
            # Inicializar repositorios
            self.codigos = CodigosAccesoRepository(s)
            self.codigos_usos = CodigosAccesoUsosRepository(s)
            self.alumnos = AlumnosRepository(s)
            self.grupos = GruposRepository(s)

            # 2. Gestión Inteligente de Transacciones
            # Si la sesión ya tiene una transacción abierta (ej: por la autenticación),
            # nos unimos a ella en lugar de abrir una nueva y causar error.
            if s.in_transaction():
                yield self
            else:
                # Si está limpia, abrimos transacción nueva
                async with s.begin():
                    try:
                        yield self
                    finally:
                        self.session = None

    @asynccontextmanager
    async def begin_nested(self) -> AsyncGenerator[UnitOfWork, None]:
        """Subtransacción (SAVEPOINT)."""
        if self.session is None:
            raise RuntimeError("UnitOfWork.begin() debe estar activo para begin_nested()")
        async with self.session.begin_nested():
            yield self

    @property
    def session_required(self) -> AsyncSession:
        if self.session is None:
            raise RuntimeError("UnitOfWork.begin() no ha sido iniciado")
        return cast(AsyncSession, self.session)

    async def commit(self):
        """Helper para casos de uso."""
        if self.session:
            await self.session.commit()

    async def rollback(self):
        """Helper para casos de uso."""
        if self.session:
            await self.session.rollback()


# ---------------------------------------------------------------------------
# FastAPI: dependencia para 1 UoW transaccional por request
# ---------------------------------------------------------------------------
async def get_uow(session_factory: async_sessionmaker[AsyncSession]) -> AsyncIterator[UnitOfWork]:
    """
    Ejemplo de integración:

        from fastapi import Depends
        from app.infrastructure.db.session import AsyncSessionLocal
        from app.infrastructure.db.uow import get_uow, UnitOfWork

        @router.post("/accion")
        async def endpoint(uow: UnitOfWork = Depends(lambda: get_uow(AsyncSessionLocal))):
            # Ya estás dentro de una transacción
            repo = MiRepo(uow.session_required)
            # SELECT ... FOR UPDATE en repos será seguro aquí
            ...
    """
    uow = UnitOfWork(session_factory)
    async with uow.begin() as tx:
        yield tx

from __future__ import annotations

from typing import Generic, TypeVar, Sequence, Optional, Any, Iterable
from datetime import datetime

from sqlalchemy import (
    select,
    update as sa_update,
    delete as sa_delete,
    Select,
    exists as sa_exists,
)
from sqlalchemy.orm import noload, selectinload, joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.base import Base

T = TypeVar("T", bound=Base)


class BaseRepository(Generic[T]):
    """
    Repositorio base genérico.
    - No hace commit/rollback: usa `async with session.begin():` en los casos de uso.
    - Provee helpers para SELECT ... FOR UPDATE y operaciones comunes.
    """

    def __init__(self, session: AsyncSession, model: type[T]):
        self.session = session
        self.model = model

    # Lecturas ---------------------------------------------------------------

    async def get(self, id_: Any) -> T | None:
        return await self.session.get(self.model, id_)

    async def get_for_update(self, id_: Any) -> T | None:
        stmt: Select = select(self.model).where(self.model.id == id_).with_for_update()
        res = await self.session.execute(stmt)
        return res.scalars().first()

    async def one(self, where: Any, options: Iterable[Any] = ()) -> T | None:
        stmt: Select = select(self.model).where(where).limit(1)
        for opt in options:
            stmt = stmt.options(opt)
        res = await self.session.execute(stmt)
        return res.scalars().first()

    async def select_for_update(self, where: Any) -> T | None:
        stmt: Select = select(self.model).where(where).with_for_update()
        res = await self.session.execute(stmt)
        return res.scalars().first()

    async def exists(self, where: Any) -> bool:
        stmt = select(sa_exists(select(self.model).where(where))).scalar_subquery()
        res = await self.session.execute(select(stmt))
        return bool(res.scalar())

    async def list(
        self,
        where: Optional[Any] = None,
        limit: int = 100,
        offset: int = 0,
        order_by: Optional[Any] = None,
        options: Iterable[Any] = (),
    ) -> Sequence[T]:
        stmt: Select = select(self.model)
        if where is not None:
            stmt = stmt.where(where)
        if order_by is not None:
            stmt = stmt.order_by(order_by)
        for opt in options:
            stmt = stmt.options(opt)
        stmt = stmt.limit(limit).offset(offset)
        res = await self.session.execute(stmt)
        return res.scalars().all()

    # Escrituras -------------------------------------------------------------

    async def create(self, entity: T) -> T:
        """
        Agrega la entidad a la sesión y hace flush para disponer de la PK
        y defaults generados por la DB (server_default).
        """
        self.session.add(entity)
        await self.session.flush()
        return entity

    async def update(self, id_: Any, values: dict, touch_updated_at: bool = True) -> int:
        """
        Actualización con SQL Core (rápida). Si hay instancias del mismo modelo
        cargadas en la sesión, considera hacer `await self.session.expire_all()`
        tras invocar este método para evitar desincronización del identity map.
        """
        if touch_updated_at and "actualizado_en" in self.model.__table__.columns:
            values = {**values, "actualizado_en": datetime.utcnow()}
        stmt = sa_update(self.model).where(self.model.id == id_).values(**values)
        res = await self.session.execute(stmt)
        return res.rowcount or 0

    async def delete(self, id_: Any) -> int:
        stmt = sa_delete(self.model).where(self.model.id == id_)
        res = await self.session.execute(stmt)
        return res.rowcount or 0

    # Utilidades -------------------------------------------------------------

    @staticmethod
    def no_load() -> Any:
        """
        Helper para evitar cargar relaciones: usar con options=(noload('*'),)
        """
        return noload("*")

    @staticmethod
    def selectin(*paths: str) -> Any:
        """
        Helper para selectinload de relaciones: options=(BaseRepository.selectin('relacion'),)
        """
        return selectinload(".".join(paths))

    @staticmethod
    def joined(*paths: str) -> Any:
        """
        Helper para joinedload de relaciones: options=(BaseRepository.joined('relacion'),)
        """
        return joinedload(".".join(paths))

# app/infrastructure/db/repositories/seguridad/sede_repo.py
from __future__ import annotations
from typing import Optional, Tuple, List
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.repositories.base import BaseRepository
from app.infrastructure.db.models.seguridad.sedes import Sede as SedeModel
from app.kernel.domain.seguridad.sede_entidad import Sede as SedeDomain

class SedeRepository(BaseRepository[SedeModel]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, SedeModel)

    def _to_domain(self, m: SedeModel) -> SedeDomain:
        return SedeDomain.model_validate(m)

    async def get(self, sede_id: int) -> Optional[SedeDomain]:
        m = await super().get_by_id(sede_id)
        return self._to_domain(m) if m else None

    async def get_by_codigo(self, codigo: str) -> Optional[SedeDomain]:
        stmt = select(SedeModel).where(SedeModel.codigo == codigo).limit(1)
        res = await self.session.execute(stmt)
        m = res.scalar_one_or_none()
        return self._to_domain(m) if m else None

    async def exists(self, sede_id: int) -> bool:
        stmt = select(SedeModel.id).where(SedeModel.id == sede_id).limit(1)
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none() is not None

    async def create(self, data: dict) -> SedeDomain:
        m = SedeModel(**data)
        self.session.add(m)
        await self.session.flush()
        await self.session.refresh(m)
        return self._to_domain(m)

    async def update(self, sede_id: int, data: dict) -> Optional[SedeDomain]:
        m = await super().get_by_id(sede_id)
        if not m:
            return None
        for k, v in data.items():
            setattr(m, k, v)
        await self.session.flush()
        await self.session.refresh(m)
        return self._to_domain(m)

    async def delete_soft(self, sede_id: int) -> bool:
        m = await super().get_by_id(sede_id)
        if not m:
            return False
        m.activo = False
        await self.session.flush()
        return True

    async def list_paginated(
        self, page: int, per_page: int, activo: Optional[bool] = None
    ) -> Tuple[List[SedeDomain], int]:
        where_clause = []
        if activo is not None:
            where_clause.append(SedeModel.activo == activo)

        # total
        count_stmt = select(func.count(SedeModel.id)).where(*where_clause)
        total = (await self.session.execute(count_stmt)).scalar_one()

        # items
        stmt = (
            select(SedeModel)
            .where(*where_clause)
            .order_by(SedeModel.nombre.asc())
            .offset((page - 1) * per_page)
            .limit(per_page)
        )
        res = await self.session.execute(stmt)
        items = [self._to_domain(m) for m in res.scalars().all()]
        return items, total

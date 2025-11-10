# app/infrastructure/db/repositories/seguridad/sesiones_repo.py
from __future__ import annotations
from typing import Sequence
from sqlalchemy import select, delete, insert
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.db.repositories.base import BaseRepository
from app.infrastructure.db.models.seguridad import Sesion
from datetime import datetime

class SesionesRepository(BaseRepository[Sesion]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Sesion)

    async def crear(self, usuario_id: int, refresh_token: str, expira_en: datetime) -> None:
        await self.session.execute(insert(Sesion).values(usuario_id=usuario_id, refresh_token=refresh_token, expira_en=expira_en))

    async def listar_por_usuario(self, usuario_id: int) -> Sequence[Sesion]:
        res = await self.session.execute(select(Sesion).where(Sesion.usuario_id == usuario_id).order_by(Sesion.id.desc()))
        return list(res.scalars().all())

    async def eliminar_por_id(self, sesion_id: int) -> bool:
        res = await self.session.execute(delete(Sesion).where(Sesion.id == sesion_id))
        return res.rowcount > 0

    async def eliminar_todas(self, usuario_id: int) -> int:
        res = await self.session.execute(delete(Sesion).where(Sesion.usuario_id == usuario_id))
        return res.rowcount or 0

    async def eliminar_por_refresh(self, refresh_token: str) -> bool:
        res = await self.session.execute(delete(Sesion).where(Sesion.refresh_token == refresh_token))
        return res.rowcount > 0

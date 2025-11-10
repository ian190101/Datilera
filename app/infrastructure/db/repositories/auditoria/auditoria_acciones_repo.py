# app/infrastructure/db/repositories/auditoria/auditoria_acciones_repo.py
from __future__ import annotations
from typing import Sequence, Optional
from datetime import datetime
from sqlalchemy import select, insert, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.db.models.auditoria.auditoria_acciones import AuditoriaAccion as AuditoriaAccionModel
from app.kernel.domain.auditoria.ports import IAuditoriaAccionRepo
from app.kernel.domain.auditoria.auditoria_accion_entidad import AuditoriaAccion

class AuditoriaAccionesRepository(IAuditoriaAccionRepo):
    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_domain(self, m: AuditoriaAccionModel) -> AuditoriaAccion:
        return AuditoriaAccion.model_validate(m)

    async def registrar(self, ev: AuditoriaAccion) -> None:
        await self.session.execute(
            insert(AuditoriaAccionModel).values(**ev.model_dump())
        )

    async def listar_por_usuario(self, usuario_id: int, *, limit: int = 100, offset: int = 0) -> Sequence[AuditoriaAccion]:
        res = await self.session.execute(
            select(AuditoriaAccionModel).where(AuditoriaAccionModel.usuario_id == usuario_id).order_by(AuditoriaAccionModel.id.desc()).limit(limit).offset(offset)
        )
        return [self._to_domain(x) for x in res.scalars().all()]

    async def listar_por_sede(self, sede_id: int, *, desde: Optional[datetime] = None, hasta: Optional[datetime] = None, limit: int = 100, offset: int = 0) -> Sequence[AuditoriaAccion]:
        conds = [AuditoriaAccionModel.sede_id == sede_id]
        if desde:
            conds.append(AuditoriaAccionModel.creado_en >= desde)
        if hasta:
            conds.append(AuditoriaAccionModel.creado_en <= hasta)
        res = await self.session.execute(
            select(AuditoriaAccionModel).where(and_(*conds)).order_by(AuditoriaAccionModel.id.desc()).limit(limit).offset(offset)
        )
        return [self._to_domain(x) for x in res.scalars().all()]

    async def listar_por_entidad(self, entidad: str, *, entidad_id: Optional[str] = None, limit: int = 100, offset: int = 0) -> Sequence[AuditoriaAccion]:
        conds = [AuditoriaAccionModel.entidad == entidad]
        if entidad_id:
            conds.append(AuditoriaAccionModel.entidad_id == entidad_id)
        res = await self.session.execute(
            select(AuditoriaAccionModel).where(and_(*conds)).order_by(AuditoriaAccionModel.id.desc()).limit(limit).offset(offset)
        )
        return [self._to_domain(x) for x in res.scalars().all()]

    async def listar_por_accion(self, accion: str, *, limit: int = 100, offset: int = 0) -> Sequence[AuditoriaAccion]:
        res = await self.session.execute(
            select(AuditoriaAccionModel).where(AuditoriaAccionModel.accion == accion).order_by(AuditoriaAccionModel.id.desc()).limit(limit).offset(offset)
        )
        return [self._to_domain(x) for x in res.scalars().all()]

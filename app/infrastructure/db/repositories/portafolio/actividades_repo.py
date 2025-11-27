# app/infrastructure/db/repositories/portafolio/actividades_repo.py

from __future__ import annotations

from datetime import date
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.repositories.base import BaseRepository
from app.infrastructure.db.models.portafolio.actividades import (
    Actividad,
)  


class ActividadesRepository(BaseRepository[Actividad]):
    """Repositorio de actividades de Portafolio."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Actividad)

    async def crear(
        self,
        alumno_id: Optional[int],
        grupo_id: Optional[int],
        profesora_id: int,
        fecha: date,
        titulo: str,
        descripcion: Optional[str],
    ) -> Actividad:
        actividad = Actividad(
            alumno_id=alumno_id,
            grupo_id=grupo_id,
            fecha_actividad=fecha,
            titulo=titulo,
            descripcion=descripcion,
            profesora_id = profesora_id,
        )
        return await self.create(actividad)

    async def obtener_por_id(self, actividad_id: int) -> Optional[Actividad]:
        stmt = select(Actividad).where(Actividad.id == actividad_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def listar_por_alumno(
        self,
        alumno_id: int,
        desde: Optional[date] = None,
        hasta: Optional[date] = None,
    ) -> List[Actividad]:
        stmt = select(Actividad).where(Actividad.alumno_id == alumno_id)
        if desde is not None:
            stmt = stmt.where(Actividad.fecha_actividad >= desde)
        if hasta is not None:
            stmt = stmt.where(Actividad.fecha_actividad <= hasta)
        stmt = stmt.order_by(Actividad.fecha_actividad.desc(), Actividad.id.desc())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

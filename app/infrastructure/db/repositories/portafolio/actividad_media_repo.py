# app/infrastructure/db/repositories/portafolio/actividad_media_repo.py

from __future__ import annotations

from datetime import datetime
from typing import List, Optional, cast 

from sqlalchemy import select, func, and_, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.repositories.base import BaseRepository
from app.infrastructure.db.models.portafolio.actividad_media import (
    ActividadMedia, TipoMedia
)  # modelo media [attached_file:19bf95e0-cff4-4cd3-a79f-589585ff54d5]


class ActividadMediaRepository(BaseRepository[ActividadMedia]):
    """Repositorio de archivos multimedia asociados a actividades."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, ActividadMedia)

    async def crear(
        self,
        actividad_id: int,
        tipo: str,
        url: str,
        nombre_archivo: str,
        mime: Optional[str],
        tamano_bytes: Optional[int],
    ) -> ActividadMedia:
        media = ActividadMedia(
            actividad_id=actividad_id,
            tipo=TipoMedia(tipo),
            url=url,
            nombre_archivo=nombre_archivo,
            mime=mime,
            tamano_bytes=tamano_bytes,
        )
        return await self.create(media)

    async def listar_por_actividad(self, actividad_id: int) -> List[ActividadMedia]:
        stmt = select(ActividadMedia).where(ActividadMedia.actividad_id == actividad_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def contar_por_tipo(self, actividad_id: int) -> dict[str, int]:
        """
        Devuelve un dict con conteo por tipo (foto/video) para validar límites 5/3.
        """
        stmt = (
            select(ActividadMedia.tipo, func.count(ActividadMedia.id))
            .where(ActividadMedia.actividad_id == actividad_id)
            .group_by(ActividadMedia.tipo)
        )
        result = await self.session.execute(stmt)
        rows = result.all()
        
        return {cast(TipoMedia, tipo).value: count for tipo, count in rows}

    async def actualizar_estado_y_urls(
        self,
        media_id: int,
        estado: str,
        url_marcada: Optional[str] = None,
    ) -> None:
        stmt = (
            update(ActividadMedia)
            .where(ActividadMedia.id == media_id)
            .values(estado=estado, url_marcada=url_marcada)
        )
        await self.session.execute(stmt)

    async def registrar_descarga(
        self,
        media_id: int,
        fecha_descarga: Optional[datetime],
        fecha_eliminacion_programada: Optional[datetime],
    ) -> None:
        """
        Registra fecha de descarga y programación de borrado (+3 días).
        La lógica de cálculo se hace en el caso de uso; aquí solo se persiste.
        """
        stmt = (
            update(ActividadMedia)
            .where(ActividadMedia.id == media_id)
            .values(
                fecha_descarga=fecha_descarga,
                fecha_eliminacion_programada=fecha_eliminacion_programada,
            )
        )
        await self.session.execute(stmt)

    async def listar_para_borrado(self, ahora: datetime) -> List[ActividadMedia]:
        """
        Devuelve media vencida según fecha_eliminacion_programada.
        """
        stmt = select(ActividadMedia).where(
            and_(
                ActividadMedia.fecha_eliminacion_programada.is_not(None),
                ActividadMedia.fecha_eliminacion_programada <= ahora,
            )
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

# app/infrastructure/db/repositories/portafolio/actividad_media_repo.py

from __future__ import annotations

from datetime import datetime
from typing import List, Optional, cast 

from sqlalchemy import select, func, and_, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.repositories.base import BaseRepository
from app.infrastructure.db.models.portafolio.actividad_media import (
    ActividadMedia, TipoMedia, EstadoProcesamientoWatermark
)  


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
    
    # ========================================================================
    # NUEVOS MÉTODOS PARA PROCESAMIENTO DE MARCA DE AGUA
    # ========================================================================
    
    async def actualizar_estado_procesamiento(
        self,
        media_id: int,
        estado_procesamiento: EstadoProcesamientoWatermark,
        cola_id: Optional[str] = None,
        error_procesamiento: Optional[str] = None,
        url_marcada: Optional[str] = None,
        procesado_en: Optional[datetime] = None,
    ) -> None:
        """
        Actualiza el estado de procesamiento de marca de agua de un archivo.
        """
        valores = {"estado_procesamiento": estado_procesamiento}
        
        if cola_id is not None:
            valores["cola_id"] = cola_id
        
        if error_procesamiento is not None:
            valores["error_procesamiento"] = error_procesamiento
            # Incrementar intentos solo cuando hay error
            stmt_intentos = (
                update(ActividadMedia)
                .where(ActividadMedia.id == media_id)
                .values(intentos_procesamiento=ActividadMedia.intentos_procesamiento + 1)
            )
            await self.session.execute(stmt_intentos)
        
        if url_marcada is not None:
            valores["url_marcada"] = url_marcada
        
        if procesado_en is not None:
            valores["procesado_en"] = procesado_en
        
        stmt = (
            update(ActividadMedia)
            .where(ActividadMedia.id == media_id)
            .values(**valores)
        )
        await self.session.execute(stmt)
    
    async def listar_por_estado_procesamiento(
        self,
        estados: List[EstadoProcesamientoWatermark],
        limite: int = 50,
    ) -> List[ActividadMedia]:
        """
        Lista archivos por estado(s) de procesamiento.
        """
        stmt = (
            select(ActividadMedia)
            .where(ActividadMedia.estado_procesamiento.in_(estados))
            .order_by(ActividadMedia.creado_en)
            .limit(limite)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def listar_errores_reintentables(
        self,
        max_intentos: int = 3,
    ) -> List[ActividadMedia]:
        """
        Lista archivos con error que aún pueden reintentarse.
        """
        stmt = select(ActividadMedia).where(
            and_(
                ActividadMedia.estado_procesamiento == EstadoProcesamientoWatermark.error,
                ActividadMedia.intentos_procesamiento < max_intentos,
            )
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def resetear_para_reprocesar(
        self,
        media_id: int,
        nueva_cola_id: str,
    ) -> None:
        """
        Resetea el estado de un archivo para reprocesarlo.
        Incrementa intentos y limpia errores.
        """
        stmt = (
            update(ActividadMedia)
            .where(ActividadMedia.id == media_id)
            .values(
                estado_procesamiento=EstadoProcesamientoWatermark.pendiente,
                cola_id=nueva_cola_id,
                error_procesamiento=None,
                intentos_procesamiento=ActividadMedia.intentos_procesamiento + 1,
            )
        )
        await self.session.execute(stmt)
    
    async def obtener_por_cola_id(self, cola_id: str) -> Optional[ActividadMedia]:
        """
        Obtiene un archivo multimedia por su ID de cola.
        Útil para actualizar desde workers de Celery/RQ.
        """
        stmt = select(ActividadMedia).where(ActividadMedia.cola_id == cola_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def contar_por_estado_procesamiento(self) -> dict[str, int]:
        """
        Devuelve conteo de archivos por estado de procesamiento.
        Útil para dashboard/monitoreo.
        """
        stmt = (
            select(
                ActividadMedia.estado_procesamiento,
                func.count(ActividadMedia.id)
            )
            .group_by(ActividadMedia.estado_procesamiento)
        )
        result = await self.session.execute(stmt)
        rows = result.all()
        return {
            cast(EstadoProcesamientoWatermark, estado).value: count 
            for estado, count in rows
        }
    
    async def obtener_por_id(self, media_id: int) -> Optional[ActividadMedia]:
        stmt = select(ActividadMedia).where(ActividadMedia.id == media_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def marcar_como_procesado(self, media_id: int) -> None:
        stmt = (
            update(ActividadMedia)
            .where(ActividadMedia.id == media_id)
            .values(procesado=True)
        )
        await self.session.execute(stmt)

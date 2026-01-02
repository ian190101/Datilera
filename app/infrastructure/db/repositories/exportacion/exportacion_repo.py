# app/infrastructure/db/repositories/exportacion/exportacion_repo.py

from __future__ import annotations
from datetime import datetime, date
from typing import List, Optional, Dict, Any

from sqlalchemy import select, update, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.repositories.base import BaseRepository
from app.infrastructure.db.models.exportacion.exportacion import (
    Exportacion,
    PlantillaExportacion,
    TipoReporte,
    FormatoArchivo,
    EstadoExportacion,
)


class ExportacionRepository(BaseRepository[Exportacion]):
    """Repositorio para gestión de exportaciones."""
    
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Exportacion)
    
    async def crear_exportacion(
        self,
        usuario_id: int,
        sede_id: int,
        tipo_reporte: TipoReporte,
        formato: FormatoArchivo,
        filtros: Optional[Dict[str, Any]] = None,
        plantilla_id: Optional[int] = None,
    ) -> Exportacion:
        """Crea un nuevo registro de exportación."""
        timestamp = int(datetime.now().timestamp())
        nombre_archivo = f"{tipo_reporte.value}_{timestamp}.{formato.value}"
        
        exportacion = Exportacion(
            usuario_id=usuario_id,
            sede_id=sede_id,
            tipo_reporte=tipo_reporte,
            formato=formato,
            filtros=filtros,
            plantilla_id=plantilla_id,
            nombre_archivo=nombre_archivo,
            estado=EstadoExportacion.PENDIENTE,
        )
        
        return await self.create(exportacion)
    
    async def obtener_por_id(self, exportacion_id: int) -> Optional[Exportacion]:
        """Obtiene una exportación por ID."""
        return await self.get_by_id(exportacion_id)
    
    async def actualizar_estado(
        self,
        exportacion_id: int,
        estado: EstadoExportacion,
        url_descarga: Optional[str] = None,
        ruta_archivo: Optional[str] = None,
        tamano_bytes: Optional[int] = None,
        error_mensaje: Optional[str] = None,
    ) -> None:
        """Actualiza el estado de una exportación."""
        valores = {
            "estado": estado,
            "procesado_en": datetime.now() if estado in [EstadoExportacion.COMPLETADO, EstadoExportacion.ERROR] else None,
        }
        
        if url_descarga:
            valores["url_descarga"] = url_descarga
        if ruta_archivo:
            valores["ruta_archivo"] = ruta_archivo
        if tamano_bytes:
            valores["tamano_bytes"] = tamano_bytes
        if error_mensaje:
            valores["error_mensaje"] = error_mensaje
        
        stmt = update(Exportacion).where(
            Exportacion.id == exportacion_id
        ).values(**valores)
        
        await self.session.execute(stmt)
    
    async def listar_por_usuario(
        self,
        usuario_id: int,
        limite: int = 20,
    ) -> List[Exportacion]:
        """Lista exportaciones de un usuario."""
        stmt = (
            select(Exportacion)
            .where(Exportacion.usuario_id == usuario_id)
            .order_by(Exportacion.solicitado_en.desc())
            .limit(limite)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def incrementar_descargas(self, exportacion_id: int) -> None:
        """Incrementa el contador de descargas."""
        stmt = update(Exportacion).where(
            Exportacion.id == exportacion_id
        ).values(
            veces_descargado=Exportacion.veces_descargado + 1,
            ultima_descarga=datetime.now(),
        )
        await self.session.execute(stmt)
    
    async def eliminar_exportacion(self, exportacion_id: int) -> None:
        """Elimina una exportación."""
        await self.delete(exportacion_id)


class PlantillaExportacionRepository(BaseRepository[PlantillaExportacion]):
    """Repositorio para gestión de plantillas de exportación."""
    
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, PlantillaExportacion)
    
    async def crear_plantilla(
        self,
        nombre: str,
        descripcion: Optional[str],
        tipo_reporte: TipoReporte,
        formato_default: FormatoArchivo,
        columnas_incluidas: List[str],
        filtros_default: Optional[Dict[str, Any]],
        creado_por: int,
        es_publica: bool = True,
    ) -> PlantillaExportacion:
        """Crea una nueva plantilla."""
        plantilla = PlantillaExportacion(
            nombre=nombre,
            descripcion=descripcion,
            tipo_reporte=tipo_reporte,
            formato_default=formato_default,
            columnas_incluidas=columnas_incluidas,
            filtros_default=filtros_default,
            creado_por=creado_por,
            es_publica=1 if es_publica else 0,
        )
        return await self.create(plantilla)
    
    async def listar_plantillas(
        self,
        tipo_reporte: Optional[TipoReporte] = None,
        solo_publicas: bool = True,
        usuario_id: Optional[int] = None,
    ) -> List[PlantillaExportacion]:
        """Lista plantillas según filtros."""
        condiciones = [PlantillaExportacion.activa == 1]
        
        if tipo_reporte:
            condiciones.append(PlantillaExportacion.tipo_reporte == tipo_reporte)
        
        if solo_publicas and not usuario_id:
            condiciones.append(PlantillaExportacion.es_publica == 1)
        elif usuario_id:
            # Plantillas públicas o creadas por el usuario
            condiciones.append(
                (PlantillaExportacion.es_publica == 1) |
                (PlantillaExportacion.creado_por == usuario_id)
            )
        
        stmt = select(PlantillaExportacion).where(and_(*condiciones))
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def obtener_por_id(self, plantilla_id: int) -> Optional[PlantillaExportacion]:
        """Obtiene una plantilla por ID."""
        return await self.get_by_id(plantilla_id)

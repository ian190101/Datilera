# app/kernel/application/auditoria/auditoria_exportaciones/obtener_estadisticas_exportaciones.py

"""
Caso de Uso: Obtener Estadísticas de Exportaciones
"""
from __future__ import annotations
from datetime import datetime
from typing import Optional, Dict
from pydantic import BaseModel, Field

from app.infrastructure.db.repositories.auditoria import AuditoriaExportacionesRepository


# ===== DTOs =====

class ObtenerEstadisticasExportacionesDTO(BaseModel):
    """DTO para obtener estadísticas de exportaciones."""
    usuario_id: Optional[int] = Field(None, gt=0)
    sede_id: Optional[int] = Field(None, gt=0)
    desde: Optional[datetime] = None
    hasta: Optional[datetime] = None


class ObtenerTotalRegistrosExportadosDTO(BaseModel):
    """DTO para total de registros exportados."""
    usuario_id: Optional[int] = Field(None, gt=0)
    tipo: Optional[str] = Field(None, max_length=50)
    desde: Optional[datetime] = None
    hasta: Optional[datetime] = None


# ===== Caso de Uso =====

class ObtenerEstadisticasExportacionesCU:
    """
    Caso de Uso: Obtener Estadísticas de Exportaciones.
    
    Responsabilidad: Generar métricas de exportaciones.
    """
    
    def __init__(self, repo: AuditoriaExportacionesRepository):
        self.repo = repo
    
    async def por_tipo(self, dto: ObtenerEstadisticasExportacionesDTO) -> Dict[str, int]:
        """Cuenta exportaciones agrupadas por tipo."""
        return await self.repo.contar_por_tipo(
            usuario_id=dto.usuario_id,
            sede_id=dto.sede_id,
            desde=dto.desde,
            hasta=dto.hasta
        )
    
    async def por_formato(
        self,
        tipo: Optional[str] = None,
        desde: Optional[datetime] = None,
        hasta: Optional[datetime] = None
    ) -> Dict[str, int]:
        """Cuenta exportaciones agrupadas por formato."""
        return await self.repo.contar_por_formato(
            tipo=tipo,
            desde=desde,
            hasta=hasta
        )
    
    async def total_registros_exportados(
        self,
        dto: ObtenerTotalRegistrosExportadosDTO
    ) -> int:
        """Suma total de registros exportados."""
        return await self.repo.obtener_total_registros_exportados(
            usuario_id=dto.usuario_id,
            tipo=dto.tipo,
            desde=dto.desde,
            hasta=dto.hasta
        )

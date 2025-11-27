# app/kernel/application/auditoria/auditoria_acciones/obtener_estadisticas.py

"""
Caso de Uso: Obtener Estadísticas de Auditoría
"""
from __future__ import annotations
from datetime import datetime
from typing import Optional, Dict, List, Any
from pydantic import BaseModel, Field

from app.infrastructure.db.repositories.auditoria import AuditoriaAccionesRepository


# ===== DTOs =====

class ObtenerEstadisticasDTO(BaseModel):
    """DTO para obtener estadísticas."""
    sede_id: Optional[int] = Field(None, gt=0)
    desde: Optional[datetime] = None
    hasta: Optional[datetime] = None


class ObtenerActividadPorHoraDTO(BaseModel):
    """DTO para actividad por hora."""
    sede_id: Optional[int] = Field(None, gt=0)
    fecha: Optional[datetime] = None


class ObtenerUsuariosMasActivosDTO(BaseModel):
    """DTO para usuarios más activos."""
    sede_id: Optional[int] = Field(None, gt=0)
    desde: Optional[datetime] = None
    hasta: Optional[datetime] = None
    limit: int = Field(default=10, ge=1, le=50)


class ObtenerErroresPorEndpointDTO(BaseModel):
    """DTO para errores por endpoint."""
    desde: Optional[datetime] = None
    hasta: Optional[datetime] = None
    limit: int = Field(default=10, ge=1, le=50)


# ===== Caso de Uso =====

class ObtenerEstadisticasCU:
    """
    Caso de Uso: Obtener Estadísticas de Auditoría.
    
    Responsabilidad: Generar métricas y agregaciones de eventos.
    """
    
    def __init__(self, repo: AuditoriaAccionesRepository):
        self.repo = repo
    
    async def por_accion(self, dto: ObtenerEstadisticasDTO) -> Dict[str, int]:
        """Cuenta eventos agrupados por acción."""
        return await self.repo.contar_por_accion(
            sede_id=dto.sede_id,
            desde=dto.desde,
            hasta=dto.hasta
        )
    
    async def por_entidad(self, dto: ObtenerEstadisticasDTO) -> Dict[str, int]:
        """Cuenta eventos agrupados por entidad."""
        return await self.repo.contar_por_entidad(
            sede_id=dto.sede_id,
            desde=dto.desde,
            hasta=dto.hasta
        )
    
    async def actividad_por_hora(self, dto: ObtenerActividadPorHoraDTO) -> List[Dict[str, Any]]:
        """Obtiene actividad agrupada por hora del día."""
        return await self.repo.obtener_actividad_por_hora(
            sede_id=dto.sede_id,
            fecha=dto.fecha
        )
    
    async def usuarios_mas_activos(self, dto: ObtenerUsuariosMasActivosDTO) -> List[Dict[str, Any]]:
        """Obtiene top usuarios más activos."""
        return await self.repo.obtener_usuarios_mas_activos(
            sede_id=dto.sede_id,
            desde=dto.desde,
            hasta=dto.hasta,
            limit=dto.limit
        )
    
    async def errores_por_endpoint(self, dto: ObtenerErroresPorEndpointDTO) -> List[Dict[str, Any]]:
        """Obtiene top endpoints con más errores."""
        return await self.repo.contar_errores_por_endpoint(
            desde=dto.desde,
            hasta=dto.hasta,
            limit=dto.limit
        )
    
    async def duracion_promedio_endpoint(
        self,
        endpoint: str,
        desde: Optional[datetime] = None,
        hasta: Optional[datetime] = None
    ) -> Optional[float]:
        """Calcula duración promedio de un endpoint."""
        return await self.repo.obtener_duracion_promedio_por_endpoint(
            endpoint=endpoint,
            desde=desde,
            hasta=hasta
        )

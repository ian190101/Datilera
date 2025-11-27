# app/kernel/application/auditoria/auditoria_prompts_ia/obtener_estadisticas_ia.py

"""
Caso de Uso: Obtener Estadísticas de IA
"""
from __future__ import annotations
from datetime import datetime
from typing import Optional, Dict, List, Any
from pydantic import BaseModel, Field

from app.infrastructure.db.repositories.auditoria import AuditoriaPromptsIARepository


# ===== DTOs =====

class ObtenerEstadisticasIADTO(BaseModel):
    """DTO para obtener estadísticas de IA."""
    usuario_id: Optional[int] = Field(None, gt=0)
    desde: Optional[datetime] = None
    hasta: Optional[datetime] = None


class ObtenerDuracionPromedioDTO(BaseModel):
    """DTO para duración promedio."""
    categoria: Optional[str] = Field(None, max_length=50)
    modelo: Optional[str] = Field(None, max_length=50)


class ObtenerUsuariosMasActivosIADTO(BaseModel):
    """DTO para usuarios más activos en IA."""
    desde: Optional[datetime] = None
    hasta: Optional[datetime] = None
    limit: int = Field(default=10, ge=1, le=50)


# ===== Caso de Uso =====

class ObtenerEstadisticasIACU:
    """
    Caso de Uso: Obtener Estadísticas de IA.
    
    Responsabilidad: Generar métricas de uso de IA.
    """
    
    def __init__(self, repo: AuditoriaPromptsIARepository):
        self.repo = repo
    
    async def por_categoria(self, dto: ObtenerEstadisticasIADTO) -> Dict[str, int]:
        """Cuenta prompts agrupados por categoría."""
        return await self.repo.contar_por_categoria(
            usuario_id=dto.usuario_id,
            desde=dto.desde,
            hasta=dto.hasta
        )
    
    async def por_modelo(
        self,
        desde: Optional[datetime] = None,
        hasta: Optional[datetime] = None
    ) -> Dict[str, int]:
        """Cuenta prompts agrupados por modelo de IA."""
        return await self.repo.contar_por_modelo(
            desde=desde,
            hasta=hasta
        )
    
    async def duracion_promedio(self, dto: ObtenerDuracionPromedioDTO) -> Optional[float]:
        """Calcula duración promedio de consultas (segundos)."""
        return await self.repo.obtener_duracion_promedio(
            categoria=dto.categoria,
            modelo=dto.modelo
        )
    
    async def usuarios_mas_activos(self, dto: ObtenerUsuariosMasActivosIADTO) -> List[Dict[str, Any]]:
        """Obtiene top usuarios con más consultas a IA."""
        return await self.repo.obtener_usuarios_mas_activos(
            desde=dto.desde,
            hasta=dto.hasta,
            limit=dto.limit
        )

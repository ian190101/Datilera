# app/kernel/application/auditoria/auditoria_sesiones/cerrar_sesiones_inactivas.py

"""
Caso de Uso: Cerrar Sesiones Inactivas
"""
from __future__ import annotations
from pydantic import BaseModel, Field

from app.infrastructure.db.repositories.auditoria import AuditoriaSesionesRepository


# ===== DTO =====

class CerrarSesionesInactivasDTO(BaseModel):
    """DTO para cerrar sesiones inactivas."""
    timeout_minutos: int = Field(default=30, ge=5, le=1440)  # Entre 5 min y 24 horas


# ===== Caso de Uso =====

class CerrarSesionesInactivasCU:
    """
    Caso de Uso: Cerrar Sesiones Inactivas.
    
    Responsabilidad: Cerrar sesiones que llevan tiempo sin actividad.
    Este CU debe ejecutarse periódicamente (tarea programada cada 5-10 minutos).
    """
    
    def __init__(self, repo: AuditoriaSesionesRepository):
        self.repo = repo
    
    async def ejecutar(self, dto: CerrarSesionesInactivasDTO) -> int:
        """
        Cierra sesiones que no tienen heartbeat reciente.
        
        Args:
            dto: Configuración de timeout
            
        Returns:
            Cantidad de sesiones cerradas
        """
        cantidad_cerrada = await self.repo.cerrar_inactivas(
            timeout_minutos=dto.timeout_minutos
        )
        
        return cantidad_cerrada

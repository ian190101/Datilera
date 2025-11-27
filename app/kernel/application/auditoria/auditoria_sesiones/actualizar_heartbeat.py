# app/kernel/application/auditoria/auditoria_sesiones/actualizar_heartbeat.py

"""
Caso de Uso: Actualizar Heartbeat de Sesión
"""
from __future__ import annotations
from pydantic import BaseModel, Field

from app.infrastructure.db.repositories.auditoria import AuditoriaSesionesRepository


# ===== DTO =====

class ActualizarHeartbeatDTO(BaseModel):
    """DTO para actualizar heartbeat."""
    sesion_id: int = Field(..., gt=0)


# ===== Caso de Uso =====

class ActualizarHeartbeatCU:
    """
    Caso de Uso: Actualizar Heartbeat de Sesión.
    
    Responsabilidad: Actualizar timestamp de última actividad de una sesión.
    Se debe llamar periódicamente (cada 1-5 minutos) para mantener la sesión viva.
    """
    
    def __init__(self, repo: AuditoriaSesionesRepository):
        self.repo = repo
    
    async def ejecutar(self, dto: ActualizarHeartbeatDTO) -> None:
        """
        Actualiza el heartbeat de una sesión.
        
        Args:
            dto: ID de la sesión
        """
        await self.repo.actualizar_heartbeat(sesion_id=dto.sesion_id)

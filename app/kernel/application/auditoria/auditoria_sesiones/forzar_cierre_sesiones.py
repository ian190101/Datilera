# app/kernel/application/auditoria/auditoria_sesiones/forzar_cierre_sesiones.py

"""
Caso de Uso: Forzar Cierre de Sesiones
"""
from __future__ import annotations
from pydantic import BaseModel, Field

from app.infrastructure.db.repositories.auditoria import AuditoriaSesionesRepository


# ===== DTO =====

class ForzarCierreSesionesDTO(BaseModel):
    """DTO para forzar cierre de sesiones de un usuario."""
    usuario_id: int = Field(..., gt=0)


# ===== Caso de Uso =====

class ForzarCierreSesionesCU:
    """
    Caso de Uso: Forzar Cierre de Sesiones de un Usuario.
    
    Responsabilidad: Cerrar todas las sesiones activas de un usuario (admin).
    Según HU: Servicio técnico debe poder forzar cierre de sesiones.
    """
    
    def __init__(self, repo: AuditoriaSesionesRepository):
        self.repo = repo
    
    async def ejecutar(self, dto: ForzarCierreSesionesDTO) -> int:
        """
        Fuerza el cierre de todas las sesiones activas de un usuario.
        
        Args:
            dto: ID del usuario
            
        Returns:
            Cantidad de sesiones cerradas
        """
        cantidad_cerrada = await self.repo.forzar_cierre_usuario(
            usuario_id=dto.usuario_id
        )
        
        return cantidad_cerrada

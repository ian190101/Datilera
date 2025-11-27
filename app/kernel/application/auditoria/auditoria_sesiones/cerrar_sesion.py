# app/kernel/application/auditoria/auditoria_sesiones/cerrar_sesion.py

"""
Caso de Uso: Cerrar Sesión
"""
from __future__ import annotations
from pydantic import BaseModel, Field

from app.kernel.domain.auditoria import AuditoriaSesion, SesionAuditoriaNoEncontrada
from app.infrastructure.db.repositories.auditoria import AuditoriaSesionesRepository


# ===== DTO =====

class CerrarSesionDTO(BaseModel):
    """DTO para cerrar sesión."""
    sesion_id: int = Field(..., gt=0)
    razon: str = Field(default="logout_manual", max_length=50)


# ===== Caso de Uso =====

class CerrarSesionCU:
    """
    Caso de Uso: Cerrar Sesión.
    
    Responsabilidad: Registrar el cierre de una sesión de usuario.
    """
    
    def __init__(self, repo: AuditoriaSesionesRepository):
        self.repo = repo
    
    async def ejecutar(self, dto: CerrarSesionDTO) -> None:
        """
        Cierra una sesión de usuario.
        
        Args:
            dto: Datos del cierre
            
        Raises:
            SesionAuditoriaNoEncontrada: Si la sesión no existe
        """
        # Verificar que la sesión existe
        sesion_model = await self.repo.obtener_por_sesion_id(dto.sesion_id)
        if sesion_model is None:
            raise SesionAuditoriaNoEncontrada(dto.sesion_id)
        
        # Cerrar sesión
        await self.repo.registrar_cierre(
            sesion_id=dto.sesion_id,
            razon=dto.razon
        )

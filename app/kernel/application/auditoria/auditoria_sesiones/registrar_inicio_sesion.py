# app/kernel/application/auditoria/auditoria_sesiones/registrar_inicio_sesion.py

"""
Caso de Uso: Registrar Inicio de Sesión
"""
from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, Field

from app.kernel.domain.auditoria import AuditoriaSesion
from app.infrastructure.db.repositories.auditoria import AuditoriaSesionesRepository


# ===== DTO =====

class RegistrarInicioSesionDTO(BaseModel):
    """DTO para registrar inicio de sesión."""
    sesion_id: int = Field(..., gt=0)
    usuario_id: int = Field(..., gt=0)
    sede_id: Optional[int] = Field(None, gt=0)
    ip: Optional[str] = Field(None, max_length=50)
    user_agent: Optional[str] = Field(None, max_length=500)
    dispositivo_tipo: Optional[str] = Field(None, max_length=20)


# ===== Caso de Uso =====

class RegistrarInicioSesionCU:
    """
    Caso de Uso: Registrar Inicio de Sesión.
    
    Responsabilidad: Registrar cuando un usuario inicia sesión.
    Según HU: Necesario para "ver quiénes están conectados" (servicio técnico).
    """
    
    def __init__(self, repo: AuditoriaSesionesRepository):
        self.repo = repo
    
    async def ejecutar(self, dto: RegistrarInicioSesionDTO) -> AuditoriaSesion:
        """
        Registra el inicio de una sesión de usuario.
        
        Args:
            dto: Datos de la sesión
            
        Returns:
            Entidad de dominio AuditoriaSesion
        """
        # Registrar en infraestructura
        model = await self.repo.registrar_inicio(
            sesion_id=dto.sesion_id,
            usuario_id=dto.usuario_id,
            sede_id=dto.sede_id,
            ip=dto.ip,
            user_agent=dto.user_agent,
            dispositivo_tipo=dto.dispositivo_tipo,
        )
        
        # Mapear a entidad de dominio
        return AuditoriaSesion.model_validate(model)

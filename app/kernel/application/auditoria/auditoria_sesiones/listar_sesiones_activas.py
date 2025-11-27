# app/kernel/application/auditoria/auditoria_sesiones/listar_sesiones_activas.py

"""
Caso de Uso: Listar Sesiones Activas
"""
from __future__ import annotations
from typing import Optional, List
from pydantic import BaseModel, Field

from app.kernel.domain.auditoria import AuditoriaSesion
from app.infrastructure.db.repositories.auditoria import AuditoriaSesionesRepository


# ===== DTO =====

class ListarSesionesActivasDTO(BaseModel):
    """DTO para listar sesiones activas."""
    sede_id: Optional[int] = Field(None, gt=0)
    usuario_id: Optional[int] = Field(None, gt=0)


# ===== Caso de Uso =====

class ListarSesionesActivasCU:
    """
    Caso de Uso: Listar Sesiones Activas.
    
    Responsabilidad: Obtener lista de sesiones activas en el sistema.
    Según HU: "Ver quiénes están conectados en el sistema" (servicio técnico).
    """
    
    def __init__(self, repo: AuditoriaSesionesRepository):
        self.repo = repo
    
    async def ejecutar(self, dto: ListarSesionesActivasDTO) -> List[AuditoriaSesion]:
        """
        Lista sesiones activas con filtros opcionales.
        
        Args:
            dto: Filtros de búsqueda
            
        Returns:
            Lista de entidades AuditoriaSesion activas
        """
        models = await self.repo.listar_activas(
            sede_id=dto.sede_id,
            usuario_id=dto.usuario_id
        )
        
        return [AuditoriaSesion.model_validate(m) for m in models]

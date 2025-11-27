# app/kernel/application/auditoria/auditoria_cambios/listar_cambios.py

"""
Caso de Uso: Listar Cambios
"""
from __future__ import annotations
from typing import List, Optional
from pydantic import BaseModel, Field

from app.kernel.domain.auditoria import AuditoriaCambio
from app.infrastructure.db.repositories.auditoria import AuditoriaCambiosRepository


# ===== DTOs =====

class ListarCambiosPorAccionDTO(BaseModel):
    """DTO para listar cambios de una acción."""
    auditoria_accion_id: int = Field(..., gt=0)


class ObtenerCambioPorCampoDTO(BaseModel):
    """DTO para obtener cambio de un campo específico."""
    auditoria_accion_id: int = Field(..., gt=0)
    campo: str = Field(..., min_length=1, max_length=100)


# ===== Caso de Uso =====

class ListarCambiosCU:
    """
    Caso de Uso: Listar Cambios.
    
    Responsabilidad: Recuperar historial de cambios de una acción.
    """
    
    def __init__(self, repo: AuditoriaCambiosRepository):
        self.repo = repo
    
    async def por_accion(self, dto: ListarCambiosPorAccionDTO) -> List[AuditoriaCambio]:
        """
        Lista todos los cambios de una acción de auditoría.
        
        Args:
            dto: ID de la acción
            
        Returns:
            Lista de entidades AuditoriaCambio
        """
        models = await self.repo.listar_por_accion(
            auditoria_accion_id=dto.auditoria_accion_id
        )
        
        return [AuditoriaCambio.model_validate(m) for m in models]
    
    async def por_campo(self, dto: ObtenerCambioPorCampoDTO) -> Optional[AuditoriaCambio]:
        """
        Obtiene el cambio de un campo específico.
        
        Args:
            dto: ID de acción y nombre del campo
            
        Returns:
            Entidad AuditoriaCambio o None si no existe
        """
        model = await self.repo.listar_por_campo(
            auditoria_accion_id=dto.auditoria_accion_id,
            campo=dto.campo
        )
        
        if model is None:
            return None
        
        return AuditoriaCambio.model_validate(model)

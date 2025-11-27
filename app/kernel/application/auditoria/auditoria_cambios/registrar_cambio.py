# app/kernel/application/auditoria/auditoria_cambios/registrar_cambio.py

"""
Caso de Uso: Registrar Cambio Individual
"""
from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, Field

from app.kernel.domain.auditoria import AuditoriaCambio
from app.infrastructure.db.repositories.auditoria import AuditoriaCambiosRepository


# ===== DTO =====

class RegistrarCambioDTO(BaseModel):
    """DTO para registrar un cambio individual."""
    auditoria_accion_id: int = Field(..., gt=0)
    campo: str = Field(..., min_length=1, max_length=100)
    valor_anterior: Optional[str] = None
    valor_nuevo: Optional[str] = None
    tipo_dato: Optional[str] = Field(None, max_length=50)


# ===== Caso de Uso =====

class RegistrarCambioCU:
    """
    Caso de Uso: Registrar Cambio Individual.
    
    Responsabilidad: Registrar el cambio de un campo específico.
    Según HU: "Historial de cambios para todo" con detalle campo por campo.
    """
    
    def __init__(self, repo: AuditoriaCambiosRepository):
        self.repo = repo
    
    async def ejecutar(self, dto: RegistrarCambioDTO) -> AuditoriaCambio:
        """
        Registra un cambio individual en un campo.
        
        Args:
            dto: Datos del cambio
            
        Returns:
            Entidad de dominio AuditoriaCambio
        """
        # Registrar en infraestructura
        model = await self.repo.registrar(
            auditoria_accion_id=dto.auditoria_accion_id,
            campo=dto.campo,
            valor_anterior=dto.valor_anterior,
            valor_nuevo=dto.valor_nuevo,
            tipo_dato=dto.tipo_dato,
        )
        
        # Mapear a entidad de dominio
        return AuditoriaCambio.model_validate(model)

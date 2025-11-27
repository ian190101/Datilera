# app/kernel/application/auditoria/auditoria_cambios/registrar_cambios_multiples.py

"""
Caso de Uso: Registrar Cambios Múltiples
"""
from __future__ import annotations
from typing import List, Dict, Any
from pydantic import BaseModel, Field

from app.infrastructure.db.repositories.auditoria import AuditoriaCambiosRepository


# ===== DTO =====

class RegistrarCambiosMultiplesDTO(BaseModel):
    """DTO para registrar múltiples cambios."""
    auditoria_accion_id: int = Field(..., gt=0)
    cambios: List[Dict[str, Any]] = Field(..., min_length=1)


# ===== Caso de Uso =====

class RegistrarCambiosMultiplesCU:
    """
    Caso de Uso: Registrar Cambios Múltiples.
    
    Responsabilidad: Registrar múltiples cambios de una sola operación (bulk).
    Útil cuando se actualiza un objeto con varios campos.
    """
    
    def __init__(self, repo: AuditoriaCambiosRepository):
        self.repo = repo
    
    async def ejecutar(self, dto: RegistrarCambiosMultiplesDTO) -> None:
        """
        Registra múltiples cambios en una sola operación.
        
        Args:
            dto: Datos de los cambios
        """
        # Preparar lista de cambios con auditoria_accion_id
        cambios_preparados = []
        for cambio in dto.cambios:
            cambios_preparados.append({
                "auditoria_accion_id": dto.auditoria_accion_id,
                "campo": cambio["campo"],
                "valor_anterior": cambio.get("valor_anterior"),
                "valor_nuevo": cambio.get("valor_nuevo"),
                "tipo_dato": cambio.get("tipo_dato"),
            })
        
        # Registrar en infraestructura (bulk insert)
        await self.repo.registrar_multiples(cambios_preparados)

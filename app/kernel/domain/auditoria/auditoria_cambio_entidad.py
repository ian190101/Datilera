# app/kernel/domain/auditoria/auditoria_cambio_entidad.py

"""
Entidad de Dominio: AuditoriaCambio
Representa un cambio individual en un campo.
"""
from __future__ import annotations
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator


class AuditoriaCambio(BaseModel):
    """
    Entidad de dominio para tracking de cambios campo por campo.
    
    Inmutable: Los cambios registrados nunca se modifican.
    """
    id: int = 0
    auditoria_accion_id: int = Field(..., gt=0)
    
    # Datos del cambio
    campo: str = Field(..., min_length=1, max_length=100)
    valor_anterior: Optional[str] = None
    valor_nuevo: Optional[str] = None
    tipo_dato: Optional[str] = Field(None, max_length=50)
    
    # Metadata
    creado_en: datetime = Field(default_factory=datetime.utcnow)
    
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        from_attributes=True,
        frozen=True,  # Inmutable
    )
    
    @field_validator("tipo_dato")
    @classmethod
    def validar_tipo_dato(cls, v: Optional[str]) -> Optional[str]:
        """Valida que el tipo de dato sea válido."""
        if v is None:
            return v
        tipos_validos = {"string", "number", "boolean", "date", "datetime", "json", "array"}
        if v.lower() not in tipos_validos:
            raise ValueError(f"Tipo de dato debe ser uno de: {tipos_validos}")
        return v.lower()
    
    def hubo_cambio(self) -> bool:
        """Verifica si realmente hubo un cambio."""
        return self.valor_anterior != self.valor_nuevo
    
    def es_creacion(self) -> bool:
        """Verifica si es una creación (valor anterior es None)."""
        return self.valor_anterior is None and self.valor_nuevo is not None
    
    def es_eliminacion(self) -> bool:
        """Verifica si es una eliminación (valor nuevo es None)."""
        return self.valor_anterior is not None and self.valor_nuevo is None

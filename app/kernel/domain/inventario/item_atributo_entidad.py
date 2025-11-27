# app/kernel/domain/inventario/item_atributo_entidad.py
from __future__ import annotations
from datetime import datetime
from pydantic import BaseModel, Field, field_validator

class ItemAtributo(BaseModel):
    """
    Atributo adicional del ítem (p.ej. talla, color, marca, etc.).
    """
    id: int
    
    # Validación: item_id debe ser mayor a 0
    item_id: int = Field(..., gt=0)
    
    nombre_atributo: str
    valor_atributo: str
    
    # Se genera automáticamente al instanciar
    creado_en: datetime = Field(default_factory=datetime.utcnow)

    @field_validator('nombre_atributo')
    @classmethod
    def validar_nombre(cls, v: str) -> str:
        """Valida que el nombre no esté vacío."""
        if not (v or "").strip():
            raise ValueError("El nombre del atributo es obligatorio.")
        return v.strip()

    @field_validator('valor_atributo')
    @classmethod
    def validar_valor(cls, v: str) -> str:
        """Valida que el valor no esté vacío."""
        if not (v or "").strip():
            raise ValueError("El valor del atributo es obligatorio.")
        return v.strip()
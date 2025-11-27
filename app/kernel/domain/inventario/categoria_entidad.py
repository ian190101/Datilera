# app/kernel/domain/inventario/categoria_entidad.py
from __future__ import annotations
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator

class Categoria(BaseModel):
    """
    Entidad Categoría (pertenece a una Familia).
    """
    id: int
    
    # Validación declarativa: familia_id debe ser mayor a 0
    familia_id: int = Field(..., gt=0)
    
    nombre: str
    descripcion: Optional[str] = None
    activo: bool = True
    
    # Se genera automáticamente al instanciar
    creado_en: datetime = Field(default_factory=datetime.utcnow)

    @field_validator('nombre')
    @classmethod
    def validar_nombre(cls, v: str) -> str:
        """Valida que el nombre no esté vacío y elimina espacios extra."""
        if not (v or "").strip():
            raise ValueError("El nombre de la categoría es obligatorio.")
        return v.strip()

    # --- Comportamiento de dominio ---

    def activar(self) -> None:
        self.activo = True

    def desactivar(self) -> None:
        self.activo = False
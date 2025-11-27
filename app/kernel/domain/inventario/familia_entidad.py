# app/kernel/domain/inventario/familia_entidad.py
from __future__ import annotations
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator

class Familia(BaseModel):
    """
    Entidad Familia (agrupa categorías: uniformes, materiales, ingredientes, limpieza, activos, etc.).
    """
    id: int
    nombre: str
    descripcion: Optional[str] = None
    activo: bool = True
    
    # Se genera automáticamente al instanciar usando la fecha actual UTC
    creado_en: datetime = Field(default_factory=datetime.utcnow)

    @field_validator('nombre')
    @classmethod
    def validar_nombre(cls, v: str) -> str:
        """Valida que el nombre no esté vacío y elimina espacios al inicio/final."""
        if not (v or "").strip():
            raise ValueError("El nombre de la familia es obligatorio.")
        return v.strip()

    # --- Comportamiento de dominio ---

    def activar(self) -> None:
        self.activo = True

    def desactivar(self) -> None:
        self.activo = False
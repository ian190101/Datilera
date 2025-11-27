# app/kernel/domain/finanzas/categoria_pago_entidad.py
from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field, field_validator

class CategoriaPago(BaseModel):
    """
    Categoría de pago por sede (dinámica): mensualidad, merienda, material, almuerzo, etc.

    Historias:
    - Categorías por sede, con nombre y monto (opcional).
    - Usadas en cobros desde la tabla de niños y en reportes/arqueo/libro de caja.
    """
    id: int
    sede_id: int
    nombre: str
    descripcion: Optional[str] = None
    
    # 'ge=0' asegura que si hay monto, no sea negativo.
    # 'default=None' permite que sea opcional.
    monto_base: Optional[Decimal] = Field(default=None, ge=0, decimal_places=2)
    
    activa: bool = True
    creado_en: datetime = Field(default_factory=datetime.utcnow)

    @field_validator('nombre')
    @classmethod
    def validar_nombre(cls, v: str) -> str:
        """Valida que el nombre no esté vacío y elimina espacios extra"""
        if not (v or "").strip():
            raise ValueError("El nombre de la categoría es obligatorio.")
        return v.strip()
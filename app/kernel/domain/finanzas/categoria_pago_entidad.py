# app/kernel/domain/finanzas/categoria_pago_entidad.py
from __future__ import annotations
from dataclasses import dataclass
from decimal import Decimal
from datetime import datetime
from typing import Optional


@dataclass
class CategoriaPago:
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
    monto_base: Optional[Decimal] = None
    activa: bool = True
    creado_en: datetime = None

    def __post_init__(self):
        if not (self.nombre or "").strip():
            raise ValueError("El nombre de la categoría es obligatorio.")
        if self.monto_base is not None and Decimal(self.monto_base) < 0:
            raise ValueError("El monto base no puede ser negativo.")
        self.creado_en = self.creado_en or datetime.utcnow()
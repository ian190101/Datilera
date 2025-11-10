# app/kernel/domain/inventario/stock_sede_entidad.py
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass
class StockSede:
    """
    Stock disponible por ítem y sede.
    - `stock_minimo`: umbral para generar alertas (la generación/dispatch se hace fuera).
    """
    id: int
    item_id: int
    sede_id: int
    cantidad_disponible: Decimal
    stock_minimo: Decimal
    actualizado_en: datetime = None

    def __post_init__(self):
        if self.item_id <= 0 or self.sede_id <= 0:
            raise ValueError("item_id/sede_id inválidos.")
        if Decimal(self.cantidad_disponible) < 0:
            raise ValueError("La cantidad disponible no puede ser negativa.")
        if Decimal(self.stock_minimo) < 0:
            raise ValueError("El stock mínimo no puede ser negativo.")
        self.actualizado_en = self.actualizado_en or datetime.utcnow()

    # --- Operaciones de stock ---
    def aumentar(self, cantidad: Decimal) -> None:
        cant = Decimal(cantidad)
        if cant <= 0:
            raise ValueError("La cantidad a aumentar debe ser > 0.")
        self.cantidad_disponible += cant
        self.actualizado_en = datetime.utcnow()

    def disminuir(self, cantidad: Decimal) -> None:
        cant = Decimal(cantidad)
        if cant <= 0:
            raise ValueError("La cantidad a disminuir debe ser > 0.")
        nueva = self.cantidad_disponible - cant
        if nueva < 0:
            raise ValueError("No hay stock suficiente.")
        self.cantidad_disponible = nueva
        self.actualizado_en = datetime.utcnow()

    def debajo_minimo(self) -> bool:
        return self.cantidad_disponible <= self.stock_minimo

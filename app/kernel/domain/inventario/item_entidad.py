# app/kernel/domain/inventario/item_entidad.py
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional


@dataclass
class Item:
    """
    Entidad Item (producto/activo del inventario).
    - `codigo` es único (SKU/código interno). La generación real del código puede
      resolverse en la capa de aplicación/infraestructura; aquí se valida su presencia.
    - `unidad_medida`: 'unidad', 'kg', 'lt', etc. (catálogo configurable fuera del dominio).
    """
    id: int
    categoria_id: int
    codigo: str
    nombre: str
    precio_unitario: Decimal
    unidad_medida: str = "unidad"
    descripcion: Optional[str] = None
    activo: bool = True
    creado_en: datetime = None
    actualizado_en: Optional[datetime] = None

    def __post_init__(self):
        if self.categoria_id <= 0:
            raise ValueError("categoria_id inválido.")
        if not (self.codigo or "").strip():
            raise ValueError("El código del ítem es obligatorio.")
        if not (self.nombre or "").strip():
            raise ValueError("El nombre del ítem es obligatorio.")
        if Decimal(self.precio_unitario) < 0:
            raise ValueError("El precio unitario no puede ser negativo.")
        self.creado_en = self.creado_en or datetime.utcnow()
        self.actualizado_en = self.actualizado_en or self.creado_en

    # --- Reglas de negocio sencillas ---
    def cambiar_precio(self, nuevo_precio: Decimal) -> None:
        if Decimal(nuevo_precio) < 0:
            raise ValueError("El precio unitario no puede ser negativo.")
        self.precio_unitario = Decimal(nuevo_precio)
        self.actualizado_en = datetime.utcnow()

    def activar(self) -> None:
        if not self.activo:
            self.activo = True
            self.actualizado_en = datetime.utcnow()

    def desactivar(self) -> None:
        if self.activo:
            self.activo = False
            self.actualizado_en = datetime.utcnow()
# app/kernel/domain/inventario/item_atributo_entidad.py
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ItemAtributo:
    """
    Atributo adicional del ítem (p.ej. talla, color, marca, etc.).
    """
    id: int
    item_id: int
    nombre_atributo: str
    valor_atributo: str
    creado_en: datetime = None

    def __post_init__(self):
        if self.item_id <= 0:
            raise ValueError("item_id inválido.")
        if not (self.nombre_atributo or "").strip():
            raise ValueError("El nombre del atributo es obligatorio.")
        if not (self.valor_atributo or "").strip():
            raise ValueError("El valor del atributo es obligatorio.")
        self.creado_en = self.creado_en or datetime.utcnow()
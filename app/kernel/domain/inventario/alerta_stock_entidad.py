# app/kernel/domain/inventario/alerta_stock_entidad.py
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime


@dataclass
class AlertaStock:
    """
    Alerta por stock bajo (generada cuando `StockSede.debajo_minimo()` es True).
    """
    id: int
    item_id: int
    sede_id: int
    mensaje: str
    resuelta: bool = False
    creado_en: datetime = None
    resuelta_en: datetime | None = None

    def __post_init__(self):
        if not (self.mensaje or "").strip():
            raise ValueError("El mensaje de la alerta es obligatorio.")
        self.creado_en = self.creado_en or datetime.utcnow()

    def resolver(self) -> None:
        if self.resuelta:
            return
        self.resuelta = True
        self.resuelta_en = datetime.utcnow()
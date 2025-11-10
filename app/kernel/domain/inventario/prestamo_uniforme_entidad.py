# app/kernel/domain/inventario/prestamo_uniforme_entidad.py
from __future__ import annotations
from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional


@dataclass
class PrestamoUniforme:
    """
    Préstamo de uniformes a personal (no venta). Se espera devolución.
    """
    id: int
    alumno_id: int
    item_id: int
    fecha_prestamo: date
    devuelto: bool = False
    fecha_devolucion: Optional[date] = None
    creado_en: datetime = None
    actualizado_en: Optional[datetime] = None

    def __post_init__(self):
        if self.alumno_id <= 0 or self.item_id <= 0:
            raise ValueError("alumno_id/item_id inválidos.")
        self.creado_en = self.creado_en or datetime.utcnow()
        self.actualizado_en = self.actualizado_en or self.creado_en

    def registrar_devolucion(self, fecha: Optional[date] = None) -> None:
        if self.devuelto:
            return
        self.devuelto = True
        self.fecha_devolucion = fecha or date.today()
        self.actualizado_en = datetime.utcnow()
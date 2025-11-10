# app/kernel/domain/inventario/movimiento_stock_entidad.py
from __future__ import annotations
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Optional


class TipoMovimiento(str, Enum):
    ENTRADA = "entrada"
    SALIDA = "salida"
    TRANSFERENCIA = "transferencia"
    AJUSTE = "ajuste"


@dataclass
class MovimientoStock:
    """
    Movimiento de stock (entrada/salida/transferencia/ajuste).
    Nota del documento: se desactivó la exigencia de evidencia/ aprobación del movimiento.
    """
    id: int
    item_id: int
    sede_id: int
    tipo: TipoMovimiento
    cantidad: Decimal
    usuario_id: int
    fecha_movimiento: date
    motivo: Optional[str] = None
    referencia: Optional[str] = None
    creado_en: datetime = None

    def __post_init__(self):
        if self.item_id <= 0 or self.sede_id <= 0:
            raise ValueError("item_id/sede_id inválidos.")
        if Decimal(self.cantidad) <= 0:
            raise ValueError("La cantidad del movimiento debe ser > 0.")
        self.creado_en = self.creado_en or datetime.utcnow()
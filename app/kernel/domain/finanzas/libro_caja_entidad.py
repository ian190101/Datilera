# app/kernel/domain/finanzas/libro_caja_entidad.py
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, date
from decimal import Decimal
from enum import Enum
from typing import List, Optional


class TipoMovimiento(str, Enum):
    INGRESO = "ingreso"
    EGRESO = "egreso"


@dataclass(frozen=True)
class MovimientoCaja:
    """VO de movimiento en Libro de Caja (se registra con referencia)."""
    fecha: date
    tipo: TipoMovimiento
    categoria_id: Optional[int]
    monto: Decimal
    referencia: Optional[str] = None  # p.ej. "pago:123", "egreso:789"
    creado_en: datetime = None

    def __post_init__(self):
        if self.monto < 0:
            raise ValueError("El monto del movimiento no puede ser negativo.")
        object.__setattr__(self, "creado_en", self.creado_en or datetime.utcnow())


@dataclass
class LibroCaja:
    """
    Libro de caja mensual y por gestión.

    Historias:
    - Se genera reporte (PDF/Excel) el día 6 del mes siguiente (servicio externo).
    - Permite agregar ingresos/egresos y consolidar totales.
    """
    id: int
    sede_id: int
    periodo_inicio: date
    periodo_fin: date
    movimientos: List[MovimientoCaja] = field(default_factory=list)
    total_ingresos: Decimal = Decimal("0.00")
    total_egresos: Decimal = Decimal("0.00")
    creado_en: datetime = None

    def __post_init__(self):
        if self.periodo_fin < self.periodo_inicio:
            raise ValueError("Rango inválido del Libro de Caja.")
        self.creado_en = self.creado_en or datetime.utcnow()

    def agregar_movimiento(self, mov: MovimientoCaja) -> None:
        if not (self.periodo_inicio <= mov.fecha <= self.periodo_fin):
            raise ValueError("Movimiento fuera del periodo del libro.")
        self.movimientos.append(mov)
        if mov.tipo == TipoMovimiento.INGRESO:
            self.total_ingresos += mov.monto
        else:
            self.total_egresos += mov.monto
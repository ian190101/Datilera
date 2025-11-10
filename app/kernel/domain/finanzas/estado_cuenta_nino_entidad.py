# app/kernel/domain/finanzas/estado_cuenta_nino_entidad.py
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, date
from decimal import Decimal
from enum import Enum
from typing import List, Optional


class TipoMovimientoCuenta(str, Enum):
    CARGO = "cargo"  # deuda: mensualidad/material/merienda/almuerzo
    ABONO = "abono"  # pago


@dataclass(frozen=True)
class MovimientoCuenta:
    """VO de movimiento del estado de cuenta por niño."""
    fecha: date
    tipo: TipoMovimientoCuenta
    categoria_id: int
    monto: Decimal
    referencia: Optional[str] = None  # p.ej. "pago:123", "cuota:456"
    creado_en: datetime = None

    def __post_init__(self):
        if Decimal(self.monto) <= 0:
            raise ValueError("El monto del movimiento debe ser > 0.")
        object.__setattr__(self, "creado_en", self.creado_en or datetime.utcnow())


class EstadoCuentaNino:
    """
    Estado de cuenta por niño.

    Historias:
    - Refleja cargos (deudas) y abonos (pagos).
    - Debe permitir ver saldo y trazabilidad por categoría/periodo.
    """

    def __init__(self, id: int, nino_id: int, sede_id: int, movimientos: Optional[List[MovimientoCuenta]] = None):
        self.id = id
        self.nino_id = nino_id
        self.sede_id = sede_id
        self.movimientos: List[MovimientoCuenta] = movimientos or []

    def agregar_cargo(self, fecha: date, categoria_id: int, monto: Decimal, referencia: Optional[str] = None) -> None:
        self.movimientos.append(MovimientoCuenta(fecha=fecha, tipo=TipoMovimientoCuenta.CARGO,
                                                 categoria_id=categoria_id, monto=Decimal(monto), referencia=referencia))

    def agregar_abono(self, fecha: date, categoria_id: int, monto: Decimal, referencia: Optional[str] = None) -> None:
        self.movimientos.append(MovimientoCuenta(fecha=fecha, tipo=TipoMovimientoCuenta.ABONO,
                                                 categoria_id=categoria_id, monto=Decimal(monto), referencia=referencia))

    @property
    def saldo(self) -> Decimal:
        cargos = sum((m.monto for m in self.movimientos if m.tipo == TipoMovimientoCuenta.CARGO), Decimal("0.00"))
        abonos = sum((m.monto for m in self.movimientos if m.tipo == TipoMovimientoCuenta.ABONO), Decimal("0.00"))
        return cargos - abonos
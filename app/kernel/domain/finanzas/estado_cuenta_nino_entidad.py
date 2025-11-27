# app/kernel/domain/finanzas/estado_cuenta_nino_entidad.py
from datetime import datetime, date
from decimal import Decimal
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict, computed_field

class TipoMovimientoCuenta(str, Enum):
    CARGO = "cargo"  # deuda: mensualidad/material/merienda/almuerzo
    ABONO = "abono"  # pago

class MovimientoCuenta(BaseModel):
    """
    VO de movimiento del estado de cuenta por niño.
    Se define como inmutable (frozen) para garantizar integridad histórica.
    """
    model_config = ConfigDict(frozen=True)  # Reemplaza a @dataclass(frozen=True)

    fecha: date
    tipo: TipoMovimientoCuenta
    categoria_id: int
    # 'gt=0' (greater than) valida que el monto sea estrictamente positivo
    monto: Decimal = Field(..., gt=0, decimal_places=2)
    referencia: Optional[str] = None
    creado_en: datetime = Field(default_factory=datetime.utcnow)

class EstadoCuentaNino(BaseModel):
    """
    Estado de cuenta por niño.

    Historias:
    - Refleja cargos (deudas) y abonos (pagos).
    - Debe permitir ver saldo y trazabilidad por categoría/periodo.
    """
    id: int
    nino_id: int
    sede_id: int
    # Inicializamos la lista vacía con una factory para evitar problemas de referencia mutable
    movimientos: List[MovimientoCuenta] = Field(default_factory=list)

    @computed_field
    def saldo(self) -> Decimal:
        """
        Calcula el saldo actual (Cargos - Abonos).
        Se incluye automáticamente en la serialización JSON.
        """
        cargos = sum((m.monto for m in self.movimientos if m.tipo == TipoMovimientoCuenta.CARGO), Decimal("0.00"))
        abonos = sum((m.monto for m in self.movimientos if m.tipo == TipoMovimientoCuenta.ABONO), Decimal("0.00"))
        return cargos - abonos

    def agregar_cargo(self, fecha: date, categoria_id: int, monto: Decimal, referencia: Optional[str] = None) -> None:
        """Registra una deuda (cargo)"""
        nuevo_movimiento = MovimientoCuenta(
            fecha=fecha,
            tipo=TipoMovimientoCuenta.CARGO,
            categoria_id=categoria_id,
            monto=monto,
            referencia=referencia
        )
        self.movimientos.append(nuevo_movimiento)

    def agregar_abono(self, fecha: date, categoria_id: int, monto: Decimal, referencia: Optional[str] = None) -> None:
        """Registra un pago (abono)"""
        nuevo_movimiento = MovimientoCuenta(
            fecha=fecha,
            tipo=TipoMovimientoCuenta.ABONO,
            categoria_id=categoria_id,
            monto=monto,
            referencia=referencia
        )
        self.movimientos.append(nuevo_movimiento)
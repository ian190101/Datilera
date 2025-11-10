# app/kernel/domain/finanzas/pago_entidad.py
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional


class MetodoPago(str, Enum):
    EFECTIVO = "efectivo"
    QR = "qr"


@dataclass
class Pago:
    """
    Registro de pago (siempre con comprobante y hash validado).

    Historias:
    - Método: efectivo o QR.
    - Validación automática del monto vs. monto esperado (si aplica).
    - Se usa en libro de caja, arqueo y conciliaciones.
    """
    id: int
    sede_id: int
    categoria_id: int
    monto: Decimal
    metodo: MetodoPago
    comprobante_id: int
    creado_por_usuario_id: int
    nino_id: Optional[int] = None           # si aplica a niño
    curso_extra_id: Optional[int] = None    # si aplica a curso extra
    plan_cuota_id: Optional[int] = None     # si liquida una cuota del plan
    monto_esperado: Optional[Decimal] = None
    creado_en: datetime = None

    def __post_init__(self):
        if Decimal(self.monto) <= 0:
            raise ValueError("El monto del pago debe ser > 0.")
        if self.monto_esperado is not None and Decimal(self.monto) != Decimal(self.monto_esperado):
            raise ValueError("El monto del pago no coincide con el monto esperado.")
        self.creado_en = self.creado_en or datetime.utcnow()
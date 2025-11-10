# app/kernel/domain/cursos_extra/pago_curso_extra_entidad.py
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from decimal import Decimal
from typing import Optional


class MetodoPago(str, Enum):
    EFECTIVO = 'efectivo'
    QR = 'qr'


@dataclass
class PagoCursoExtra:
    """Entidad PagoCursoExtra (registro manual con comprobante).

    - Métodos: EFECTIVO o QR.
    - Comprobante obligatorio (imagen o PDF) y hash obligatorio (anti-duplicados).
    - Monto > 0.
    """

    id: int
    curso_id: int
    inscripcion_id: Optional[int]
    monto: Decimal
    metodo: MetodoPago
    comprobante_ruta: str
    comprobante_hash: str
    creado_por_usuario_id: int  # directora/superadmin
    creado_en: datetime = None

    def __post_init__(self):
        if Decimal(self.monto) <= 0:
            raise ValueError('El monto debe ser mayor a 0.')
        if not self.comprobante_ruta:
            raise ValueError('Se requiere ruta del comprobante.')
        if not self.comprobante_hash:
            raise ValueError('Se requiere hash del comprobante.')
        self.creado_en = self.creado_en or datetime.utcnow()
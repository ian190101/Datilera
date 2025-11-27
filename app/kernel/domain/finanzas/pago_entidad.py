# app/kernel/domain/finanzas/pago_entidad.py
from __future__ import annotations  # <--- Esto soluciona el error "Pago is not defined"
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, model_validator

class MetodoPago(str, Enum):
    EFECTIVO = "efectivo"
    QR = "qr"

class Pago(BaseModel):
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
    
    # 'gt=0' valida que sea mayor a 0. decimal_places=2 maneja la precisión.
    monto: Decimal = Field(..., gt=0, decimal_places=2)
    
    metodo: MetodoPago
    comprobante_id: int
    creado_por_usuario_id: int
    
    # Campos opcionales (default=None)
    nino_id: Optional[int] = None
    curso_extra_id: Optional[int] = None
    plan_cuota_id: Optional[int] = None
    
    monto_esperado: Optional[Decimal] = None
    
    # default_factory asigna la fecha actual si no se envía
    creado_en: datetime = Field(default_factory=datetime.utcnow)

    @model_validator(mode='after')
    def validar_monto_contra_esperado(self) -> Pago:
        """
        Si se define un monto esperado, valida que el pago coincida exactamente.
        """
        if self.monto_esperado is not None and self.monto != self.monto_esperado:
            raise ValueError(
                f"El monto del pago ({self.monto}) no coincide con el monto esperado ({self.monto_esperado})."
            )
        return self
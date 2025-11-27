# app/kernel/domain/cursosextra/pago_curso_extra_entidad.py

"""
Entidad de dominio: PagoCursoExtra
"""
from __future__ import annotations
from datetime import date
from decimal import Decimal
from enum import Enum
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator


class MetodoPagoCursoExtra(str, Enum):
    """Método de pago utilizado."""
    EFECTIVO = "efectivo"
    QR = "qr"
    TRANSFERENCIA = "transferencia"


class PagoCursoExtra(BaseModel):
    """
    Entidad **PagoCursoExtra**.
    
    Registra un pago realizado para una inscripción a curso extra.
    Cada pago se asocia a un balance y actualiza el saldo pendiente.
    
    Reglas:
    - Los pagos son inmutables una vez registrados
    - Deben tener comprobante (futuro módulo de facturación)
    - El monto debe ser positivo
    """
    id: int
    balance_curso_extra_id: int
    
    # Información del pago
    monto: Decimal
    fecha_pago: date = Field(default_factory=date.today)
    metodo_pago: MetodoPagoCursoExtra = MetodoPagoCursoExtra.EFECTIVO
    
    # Comprobante (futuro módulo)
    comprobante_url: Optional[str] = None
    numero_transaccion: Optional[str] = None
    
    # Observaciones
    observaciones: Optional[str] = None
    
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        from_attributes=True,
        frozen=True,  # Inmutable: los pagos no se editan
    )
    
    @field_validator("monto")
    @classmethod
    def _monto_valido(cls, v: Decimal) -> Decimal:
        """Valida que el monto sea positivo."""
        if v <= Decimal("0"):
            raise ValueError("El monto del pago debe ser mayor a 0.")
        return v
    
    @field_validator("observaciones")
    @classmethod
    def _observaciones_validas(cls, v: Optional[str]) -> Optional[str]:
        """Valida longitud de observaciones."""
        if v and len(v) > 500:
            raise ValueError("Las observaciones no pueden superar 500 caracteres.")
        return v
    
    # --- Comportamiento ---
    
    def tiene_comprobante(self) -> bool:
        """Verifica si tiene comprobante adjunto."""
        return self.comprobante_url is not None
    
    def es_pago_electronico(self) -> bool:
        """Verifica si es pago electrónico (QR o transferencia)."""
        return self.metodo_pago in [
            MetodoPagoCursoExtra.QR,
            MetodoPagoCursoExtra.TRANSFERENCIA
        ]

# app/kernel/domain/cursosextra/balance_curso_extra_entidad.py

"""
Entidad de dominio: BalanceCursoExtra
"""
from __future__ import annotations
from datetime import date
from decimal import Decimal
from enum import Enum
from typing import Optional
from pydantic import BaseModel, ConfigDict, field_validator


class EstadoBalance(str, Enum):
    """Estado del balance de pago."""
    PENDIENTE = "pendiente"
    PARCIAL = "parcial"
    PAGADO = "pagado"


class BalanceCursoExtra(BaseModel):
    """
    Entidad **BalanceCursoExtra**.
    
    Representa el estado de cuenta individual de una inscripción a curso extra.
    Controla el monto total, lo pagado y el saldo pendiente.
    
    Reglas:
    - Cada inscripción tiene un único balance
    - El saldo se calcula como: total - pagado
    - El estado se actualiza automáticamente según los pagos
    """
    id: int
    inscripcion_curso_extra_id: int
    
    # Montos
    monto_total: Decimal
    monto_pagado: Decimal = Decimal("0.00")
    saldo: Decimal
    
    # Control
    fecha_vencimiento: Optional[date] = None
    estado: EstadoBalance = EstadoBalance.PENDIENTE
    
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        from_attributes=True,
    )
    
    @field_validator("monto_total")
    @classmethod
    def _monto_total_valido(cls, v: Decimal) -> Decimal:
        """Valida que el monto total sea positivo."""
        if v <= Decimal("0"):
            raise ValueError("El monto total debe ser mayor a 0.")
        return v
    
    def model_post_init(self, __context) -> None:
        """Valida integridad de montos."""
        if self.monto_pagado > self.monto_total:
            raise ValueError("El monto pagado no puede exceder el monto total.")
        
        if self.saldo < Decimal("0"):
            raise ValueError("El saldo no puede ser negativo.")
    
    # --- Comportamiento ---
    
    def registrar_pago(self, monto: Decimal) -> None:
        """
        Registra un pago y actualiza el estado del balance.
        
        Reglas:
        - El pago no puede exceder el saldo pendiente
        - Actualiza automáticamente el estado según el saldo
        """
        if monto <= Decimal("0"):
            raise ValueError("El monto del pago debe ser mayor a 0.")
        
        if monto > self.saldo:
            raise ValueError(
                f"El pago ({monto}) excede el saldo pendiente ({self.saldo})."
            )
        
        self.monto_pagado += monto
        self.saldo -= monto
        
        # Actualizar estado
        self._actualizar_estado()
    
    def _actualizar_estado(self) -> None:
        """Actualiza el estado según el saldo."""
        if self.saldo == Decimal("0"):
            self.estado = EstadoBalance.PAGADO
        elif self.monto_pagado > Decimal("0"):
            self.estado = EstadoBalance.PARCIAL
        else:
            self.estado = EstadoBalance.PENDIENTE
    
    def esta_pagado(self) -> bool:
        """Verifica si está completamente pagado."""
        return self.estado == EstadoBalance.PAGADO
    
    def esta_pendiente(self) -> bool:
        """Verifica si está pendiente de pago."""
        return self.estado == EstadoBalance.PENDIENTE
    
    def tiene_pagos_parciales(self) -> bool:
        """Verifica si tiene pagos parciales."""
        return self.estado == EstadoBalance.PARCIAL
    
    def calcular_porcentaje_pagado(self) -> Decimal:
        """Calcula el porcentaje pagado."""
        if self.monto_total == Decimal("0"):
            return Decimal("0")
        return (self.monto_pagado / self.monto_total) * Decimal("100")

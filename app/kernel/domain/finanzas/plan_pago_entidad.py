# app/kernel/domain/finanzas/plan_pago_entidad.py
from __future__ import annotations
from datetime import datetime, date
from decimal import Decimal
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field, model_validator, computed_field

class ReglaInicial(str, Enum):
    CUARENTA_PORCIENTO = "40%"
    MIL_BS = "1000_bs"
    PERSONALIZADA = "personalizada"  # permite monto inicial distinto

class PlanCuota(BaseModel):
    """Entidad de cuota del plan (tabla independiente en infraestructura)."""
    id: int
    plan_id: int
    
    # Validación: Monto > 0
    monto: Decimal = Field(..., gt=0, decimal_places=2)
    vencimiento: date
    
    pagada: bool = False
    pago_id: Optional[int] = None
    
    creado_en: datetime = Field(default_factory=datetime.utcnow)
    pagada_en: Optional[datetime] = None

    def registrar_pago(self, pago_id: int, fecha: Optional[datetime] = None) -> None:
        """Método de dominio para actualizar el estado de la cuota"""
        if self.pagada:
            return
        self.pagada = True
        self.pago_id = pago_id
        self.pagada_en = fecha or datetime.utcnow()

class PlanPago(BaseModel):
    """
    Plan anual de pago para categorías dinámicas (p.ej., 'material' o 'merienda').

    Reglas (del documento):
    - Total base sugerido: 3.400 Bs (parametrizable).
    - Cuota inicial: 40% o 1.000 Bs, o personalizada.
    - Resto: cuotas mensuales variables personalizadas (sin intereses).
    - Debe permitir adelantos (marcar pagado una o varias cuotas).
    """
    id: int
    nino_id: int
    sede_id: int
    
    # Referencia a CategoriaPago. gt=0 asegura ID válido.
    categoria_id: int = Field(..., gt=0)
    
    # Default sugerido 3400, validación > 0
    total: Decimal = Field(default=Decimal("3400.00"), gt=0, decimal_places=2)
    
    regla_inicial: ReglaInicial = ReglaInicial.CUARENTA_PORCIENTO
    monto_inicial_personalizado: Optional[Decimal] = Field(default=None, decimal_places=2)
    
    # Inicializa lista vacía
    cuotas: List[PlanCuota] = Field(default_factory=list)
    creado_en: datetime = Field(default_factory=datetime.utcnow)

    @model_validator(mode='after')
    def validar_regla_personalizada(self) -> PlanPago:
        """
        Valida que si la regla es PERSONALIZADA, se haya provisto un monto inicial válido.
        """
        if self.regla_inicial == ReglaInicial.PERSONALIZADA:
            if self.monto_inicial_personalizado is None or self.monto_inicial_personalizado <= 0:
                raise ValueError("Monto inicial personalizado inválido para la regla seleccionada.")
        return self

    @computed_field
    def monto_inicial_calculado(self) -> Decimal:
        """
        Calcula el monto de la cuota inicial según la regla.
        Se incluye en la serialización JSON.
        """
        if self.regla_inicial == ReglaInicial.CUARENTA_PORCIENTO:
            return (self.total * Decimal("0.40")).quantize(Decimal("0.01"))
        
        if self.regla_inicial == ReglaInicial.MIL_BS:
            return Decimal("1000.00")
        
        return self.monto_inicial_personalizado or Decimal("0.00")

    @computed_field
    def saldo_pendiente(self) -> Decimal:
        """
        Calcula el saldo restante (Total - Inicial - Cuotas Pagadas).
        """
        # Sumamos solo las cuotas que ya están pagadas
        pagado_cuotas = sum(
            (c.monto for c in self.cuotas if c.pagada), 
            Decimal("0.00")
        )
        # El saldo es: Total Plan - Monto Inicial (que se paga al principio) - Cuotas ya abonadas
        # Nota: Asume que la 'cuota inicial' se paga aparte o se gestiona distinto a las cuotas mensuales listadas
        return self.total - self.monto_inicial_calculado - pagado_cuotas

    def agregar_cuota(self, cuota: PlanCuota) -> None:
        self.cuotas.append(cuota)

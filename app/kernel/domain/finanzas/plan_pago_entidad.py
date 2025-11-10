# app/kernel/domain/finanzas/plan_pago_entidad.py
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, date
from decimal import Decimal
from enum import Enum
from typing import List, Optional


class ReglaInicial(str, Enum):
    CUARENTA_PORCIENTO = "40%"
    MIL_BS = "1000_bs"
    PERSONALIZADA = "personalizada"  # permite monto inicial distinto


@dataclass
class PlanCuota:
    """Entidad de cuota del plan (tabla independiente en infraestructura)."""
    id: int
    plan_id: int
    monto: Decimal
    vencimiento: date
    pagada: bool = False
    pago_id: Optional[int] = None
    creado_en: datetime = None
    pagada_en: Optional[datetime] = None

    def __post_init__(self):
        if Decimal(self.monto) <= 0:
            raise ValueError("La cuota debe tener monto > 0.")
        self.creado_en = self.creado_en or datetime.utcnow()

    def registrar_pago(self, pago_id: int, fecha: Optional[datetime] = None) -> None:
        if self.pagada:
            return
        self.pagada = True
        self.pago_id = pago_id
        self.pagada_en = fecha or datetime.utcnow()


class PlanPago:
    """
    Plan anual de pago para categorías dinámicas (p.ej., 'material' o 'merienda').

    Reglas (del documento):
    - Total base sugerido: 3.400 Bs (parametrizable).
    - Cuota inicial: 40% o 1.000 Bs, o personalizada.
    - Resto: cuotas mensuales variables personalizadas (sin intereses).
    - Debe permitir adelantos (marcar pagado una o varias cuotas).

    NOTA: El tipo de plan **no es Enum**. Se referencia a la categoría creada
    dinámicamente en `CategoriaPago` mediante `categoria_id`.
    """

    def __init__(
        self,
        id: int,
        nino_id: int,
        sede_id: int,
        categoria_id: int,                     # referencia a CategoriaPago (material/merienda u otras)
        total: Decimal = Decimal("3400.00"),
        regla_inicial: ReglaInicial = ReglaInicial.CUARENTA_PORCIENTO,
        monto_inicial_personalizado: Optional[Decimal] = None,
        cuotas: Optional[List[PlanCuota]] = None,
        creado_en: Optional[datetime] = None,
    ):
        if categoria_id <= 0:
            raise ValueError("categoria_id inválido.")
        if Decimal(total) <= 0:
            raise ValueError("El total del plan debe ser > 0.")
        if (regla_inicial == ReglaInicial.PERSONALIZADA and
            (monto_inicial_personalizado is None or Decimal(monto_inicial_personalizado) <= 0)):
            raise ValueError("Monto inicial personalizado inválido.")

        self.id = id
        self.nino_id = nino_id
        self.sede_id = sede_id
        self.categoria_id = categoria_id
        self.total = Decimal(total)
        self.regla_inicial = regla_inicial
        self.monto_inicial_personalizado = (Decimal(monto_inicial_personalizado)
                                            if monto_inicial_personalizado is not None else None)
        self.cuotas: List[PlanCuota] = cuotas or []
        self.creado_en = creado_en or datetime.utcnow()

    # --- Reglas ---
    def calcular_cuota_inicial(self) -> Decimal:
        if self.regla_inicial == ReglaInicial.CUARENTA_PORCIENTO:
            return (self.total * Decimal("0.40")).quantize(Decimal("0.01"))
        if self.regla_inicial == ReglaInicial.MIL_BS:
            return Decimal("1000.00")
        return self.monto_inicial_personalizado or Decimal("0.00")

    def saldo_pendiente(self) -> Decimal:
        pagado_cuotas = sum((c.monto for c in self.cuotas if c.pagada), Decimal("0.00"))
        return self.total - self.calcular_cuota_inicial() - pagado_cuotas

    def agregar_cuota(self, cuota: PlanCuota) -> None:
        self.cuotas.append(cuota)

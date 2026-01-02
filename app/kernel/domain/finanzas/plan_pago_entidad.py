# app/kernel/domain/finanzas/plan_pago_entidad.py

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from datetime import date, datetime
from decimal import Decimal
from typing import Optional, Annotated
from dateutil.relativedelta import relativedelta


class PlanPagoEntidad(BaseModel):
    """Entidad de dominio: Plan de pago personalizado."""
    
    model_config = ConfigDict(
        from_attributes=True,       # equiv. a orm_mode / from_attributes en v1
        populate_by_name=True,      # permite usar alias si los defines
    )

    # Identificación
    id: Optional[int] = None
    alumno_id: int = Field(..., gt=0)

    # Montos base
    monto_base: Decimal = Field(default=Decimal('3400.00'), ge=0)

    # Material (opcional)
    incluye_material: bool = False
    monto_material: Decimal = Field(default=Decimal('0.00'), ge=0)

    # Merienda (opcional)
    incluye_merienda: bool = False
    monto_merienda: Decimal = Field(default=Decimal('0.00'), ge=0)

    # Total y cuotas
    monto_total: Decimal = Field(..., ge=0)
    numero_cuotas: int = Field(default=12, ge=1, le=24)
    monto_cuota: Decimal = Field(..., ge=0)

    # Vigencia
    fecha_inicio: date = Field(...)
    fecha_fin: Optional[date] = None

    # Estado
    estado: Annotated[str, Field(default='activo', pattern=r'^(activo|completado|cancelado)$')]

    # Ubicación
    sede_id: int = Field(..., gt=0)

    # Auditoría
    creado_por: int = Field(..., gt=0)
    creado_en: datetime = Field(default_factory=datetime.utcnow)
    actualizado_en: Optional[datetime] = None

    # ------------------------------------------------------------------
    # Validadores
    # ------------------------------------------------------------------

    @field_validator('monto_material')
    @classmethod
    def validar_material(cls, v: Decimal, info) -> Decimal:
        if info.data.get('incluye_material') and v <= 0:
            raise ValueError('Si incluye material, el monto debe ser mayor a 0')
        return v

    @field_validator('monto_merienda')
    @classmethod
    def validar_merienda(cls, v: Decimal, info) -> Decimal:
        if info.data.get('incluye_merienda') and v <= 0:
            raise ValueError('Si incluye merienda, el monto debe ser mayor a 0')
        return v

    @model_validator(mode='after')
    def calcular_montos(self) -> 'PlanPagoEntidad':
        """Calcula monto_total y monto_cuota automáticamente si no están definidos."""
        total = self.monto_base

        if self.incluye_material:
            total += self.monto_material
        if self.incluye_merienda:
            total += self.monto_merienda

        # Si no viene definido o es cero, lo calculamos
        if self.monto_total in (None, Decimal('0')):
            self.monto_total = total

        # Cálculo de cuota con redondeo a 2 decimales
        if self.numero_cuotas > 0:
            cuota = (self.monto_total / Decimal(self.numero_cuotas)).quantize(Decimal('0.01'))
            self.monto_cuota = cuota

        return self

    # ------------------------------------------------------------------
    # Métodos de dominio
    # ------------------------------------------------------------------

    def calcular_fecha_fin(self) -> date:
        """Fecha de finalización = fecha_inicio + numero_cuotas meses."""
        return self.fecha_inicio + relativedelta(months=self.numero_cuotas)

    def esta_activo(self) -> bool:
        return self.estado == 'activo'

    # ------------------------------------------------------------------
    # Uso típico (para que veas cómo queda la serialización perfecta)
    # ------------------------------------------------------------------

    # En tus endpoints o servicios:
    # data = plan.model_dump()                    # → objetos date/datetime (ideal para Python)
    # json_compatible = plan.model_dump(mode='json')  # → todo en strings ISO, listo para API
    # json_str = plan.model_dump_json(indent=2)   # → string JSON directo
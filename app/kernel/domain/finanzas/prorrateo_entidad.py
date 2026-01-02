# app/kernel/domain/finanzas/prorrateo_entidad.py

from pydantic import BaseModel, ConfigDict, Field, model_validator
from datetime import date, datetime
from decimal import Decimal
from typing import Optional, Self # Self es útil para model_validator
import calendar

class ProrrateoEntidad(BaseModel):
    """Entidad de dominio: Cálculo de prorrateo para primer mes."""
    
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )

    # Identificación
    id: Optional[int] = None
    alumno_id: int = Field(..., gt=0)

    # Fecha de ingreso
    fecha_ingreso: date = Field(...)

    # Cálculo
    dias_cursados: int = Field(..., ge=1, le=31)
    dias_mes: int = Field(..., ge=28, le=31)
    monto_completo: Decimal = Field(..., ge=0)
    monto_prorrateo: Decimal = Field(..., ge=0)

    # Estado
    aplicado: bool = False
    pago_id: Optional[int] = None

    # Ubicación
    sede_id: int = Field(..., gt=0)

    # Auditoría
    creado_por: Optional[int] = None
    creado_en: datetime = Field(default_factory=datetime.utcnow)
    actualizado_en: Optional[datetime] = None

    # ------------------------------------------------------------------
    # Validadores de Modelo (Consistencia entre campos)
    # ------------------------------------------------------------------

    @model_validator(mode='after')
    def validar_consistencia_logica(self) -> Self:
        # 1. Validar que dias cursados no supere dias del mes
        if self.dias_cursados > self.dias_mes:
            raise ValueError(f'Los días cursados ({self.dias_cursados}) no pueden exceder los días del mes ({self.dias_mes})')
        
        # 2. Validar que el prorrateo no sea mayor al total
        if self.monto_prorrateo > self.monto_completo:
            raise ValueError('El monto de prorrateo no puede exceder el monto completo')
            
        return self

    # ------------------------------------------------------------------
    # Factory method
    # ------------------------------------------------------------------
    @classmethod
    def calcular_prorrateo(
        cls,
        alumno_id: int,
        fecha_ingreso: date,
        monto_mensual: Decimal,
        sede_id: int,
        creado_por: Optional[int] = None,
    ) -> 'ProrrateoEntidad':
        _, dias_mes = calendar.monthrange(fecha_ingreso.year, fecha_ingreso.month)
        dias_cursados = dias_mes - fecha_ingreso.day + 1

        # Nota: Usamos round() o quantize aquí para asegurar precisión antes de instanciar
        monto_prorrateo = (monto_mensual * Decimal(dias_cursados) / Decimal(dias_mes)).quantize(Decimal('0.01'))

        return cls(
            alumno_id=alumno_id,
            fecha_ingreso=fecha_ingreso,
            dias_cursados=dias_cursados,
            dias_mes=dias_mes,
            monto_completo=monto_mensual,
            monto_prorrateo=monto_prorrateo,
            sede_id=sede_id,
            creado_por=creado_por,
        )

    # Métodos de dominio...
    def calcular_porcentaje_prorrateo(self) -> Decimal:
        if self.dias_mes == 0:
            return Decimal('0.00')
        porcentaje = (Decimal(self.dias_cursados) / Decimal(self.dias_mes)) * Decimal('100')
        return porcentaje.quantize(Decimal('0.01'))
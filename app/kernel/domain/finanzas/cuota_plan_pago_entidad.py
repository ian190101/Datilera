# app/kernel/domain/finanzas/cuota_plan_pago_entidad.py

from pydantic import BaseModel, ConfigDict, Field, field_validator
from datetime import date, datetime
from decimal import Decimal
from typing import Optional, Annotated


class CuotaPlanPagoEntidad(BaseModel):
    """Entidad de dominio: Cuota individual de un plan de pago."""
    
    model_config = ConfigDict(
        from_attributes=True,        # Reemplaza orm_mode / from_attributes
        populate_by_name=True,       # Buenas prácticas
    )

    # Identificación
    id: Optional[int] = None
    plan_id: int = Field(..., gt=0)
    numero_cuota: int = Field(..., ge=1, le=24)

    # Montos
    monto_cuota: Decimal = Field(..., ge=0)
    monto_pagado: Decimal = Field(default=Decimal('0.00'), ge=0)
    mora: Decimal = Field(default=Decimal('0.00'), ge=0)

    # Fechas
    fecha_vencimiento: date = Field(...)
    fecha_pago: Optional[datetime] = None

    # Estado
    estado: Annotated[
        str,
        Field(default='pendiente', pattern=r'^(pendiente|pagada|vencida|cancelada)$')
    ]

    # Relación con pago
    pago_id: Optional[int] = None

    # Auditoría
    creado_en: datetime = Field(default_factory=datetime.utcnow)
    actualizado_en: Optional[datetime] = None

    # ------------------------------------------------------------------
    # Validadores
    # ------------------------------------------------------------------

    @field_validator('monto_pagado')
    @classmethod
    def validar_monto_pagado(cls, v: Decimal, info) -> Decimal:
        """El monto pagado no puede exceder el monto de la cuota + mora."""
        monto_cuota = info.data.get('monto_cuota')
        mora = info.data.get('mora')
        
        if monto_cuota is not None and mora is not None:
            total_adeudado = monto_cuota + mora
            if v > total_adeudado:
                raise ValueError('El monto pagado no puede exceder el monto adeudado')
        return v

    # ------------------------------------------------------------------
    # Métodos de dominio
    # ------------------------------------------------------------------

    def esta_vencida(self, fecha_actual: Optional[date] = None) -> bool:
        """Verifica si la cuota está vencida según la fecha actual."""
        if fecha_actual is None:
            fecha_actual = date.today()
        
        return self.estado == 'pendiente' and self.fecha_vencimiento < fecha_actual

    def esta_pagada(self) -> bool:
        """Verifica si la cuota fue completamente pagada."""
        return self.estado == 'pagada' and self.monto_pagado >= self.monto_cuota

    def calcular_saldo(self) -> Decimal:
        """Saldo pendiente = cuota + mora - pagado."""
        total_adeudado = self.monto_cuota + self.mora
        saldo = total_adeudado - self.monto_pagado
        return saldo.quantize(Decimal('0.01')) if saldo > 0 else Decimal('0.00')

    def calcular_mora(
        self,
        tasa_mora_diaria: Decimal = Decimal('0.02'),  # 2%
        fecha_actual: Optional[date] = None
    ) -> Decimal:
        """
        Calcula la mora por retraso.

        Args:
            tasa_mora_diaria: Tasa diaria como decimal (0.02 = 2%)
            fecha_actual: Fecha de referencia (hoy por defecto)

        Returns:
            Monto de mora redondeado a 2 decimales
        """
        if self.estado == 'pagada':
            return Decimal('0.00')

        if fecha_actual is None:
            fecha_actual = date.today()

        if fecha_actual <= self.fecha_vencimiento:
            return Decimal('0.00')

        dias_retraso = (fecha_actual - self.fecha_vencimiento).days
        tasa_diaria = tasa_mora_diaria / Decimal('100')
        mora_bruta = self.monto_cuota * tasa_diaria * Decimal(dias_retraso)
        
        return mora_bruta.quantize(Decimal('0.01'))

    # ------------------------------------------------------------------
    # Ejemplo de uso (para que veas lo lindo que queda)
    # ------------------------------------------------------------------

    # En tus endpoints o servicios:
    # cuota.model_dump()                    # → fechas como objetos date/datetime
    # cuota.model_dump(mode='json')         # → fechas como strings ISO → "2025-11-28"
    # cuota.model_dump_json(indent=2)       # → JSON listo para enviar al frontend
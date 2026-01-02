# app/kernel/domain/finanzas/descuento_entidad.py

from pydantic import BaseModel, Field, field_validator
from datetime import date, datetime
from decimal import Decimal
from typing import Optional


class DescuentoEntidad(BaseModel):
    """Entidad de dominio: Descuento aplicado a un alumno."""
    
    # Identificación
    id: Optional[int] = None
    alumno_id: int = Field(..., gt=0)
    
    # Tipo y monto
    tipo: str = Field(..., pattern="^(semestral|anual)$")
    porcentaje: Decimal = Field(..., ge=0, le=100)
    monto_descuento: Decimal = Field(..., ge=0)
    
    # Período de vigencia
    periodo_inicio: date
    periodo_fin: date
    
    # Estado
    estado: str = Field(default='activo', pattern="^(activo|vencido|cancelado)$")
    
    # Ubicación
    sede_id: int = Field(..., gt=0)
    
    # Auditoría
    aplicado_por: int = Field(..., gt=0)
    aplicado_en: datetime = Field(default_factory=datetime.utcnow)
    creado_en: datetime = Field(default_factory=datetime.utcnow)
    actualizado_en: Optional[datetime] = None
    
    class Config:
        from_attributes = True
        json_encoders = {
            Decimal: lambda v: float(v),
            date: lambda v: v.isoformat(),
            datetime: lambda v: v.isoformat(),
        }
    
    @field_validator('periodo_fin')
    @classmethod
    def validar_periodo(cls, v: date, info) -> date:
        """Validar que periodo_fin sea posterior a periodo_inicio."""
        if 'periodo_inicio' in info.data and v <= info.data['periodo_inicio']:
            raise ValueError('periodo_fin debe ser posterior a periodo_inicio')
        return v
    
    @field_validator('porcentaje')
    @classmethod
    def validar_porcentaje_descuento(cls, v: Decimal, info) -> Decimal:
        """Validar porcentajes según tipo de descuento."""
        if 'tipo' in info.data:
            tipo = info.data['tipo']
            if tipo == 'semestral' and v != Decimal('3.00'):
                raise ValueError('Descuento semestral debe ser 3%')
            if tipo == 'anual' and v != Decimal('6.00'):
                raise ValueError('Descuento anual debe ser 6%')
        return v
    
    def esta_vigente(self, fecha_actual: Optional[date] = None) -> bool:
        """Verificar si el descuento está vigente en una fecha."""
        if fecha_actual is None:
            fecha_actual = date.today()
        
        return (
            self.estado == 'activo' and
            self.periodo_inicio <= fecha_actual <= self.periodo_fin
        )
    
    def calcular_monto_descuento(self, monto_base: Decimal) -> Decimal:
        """Calcular el monto del descuento sobre un monto base."""
        return (monto_base * self.porcentaje) / Decimal('100')

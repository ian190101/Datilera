# app/kernel/domain/finanzas/pago_entidad.py
"""
Entidad de dominio: Pago.
Representa un pago realizado por un alumno.
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional
from enum import Enum

from pydantic import BaseModel, Field, field_validator, ConfigDict


class MetodoPago(str, Enum):
    """
    Enum de métodos de pago permitidos según HU.
    Solo efectivo y QR están permitidos.
    """
    EFECTIVO = "efectivo"
    QR = "qr"
    
    @classmethod
    def valores(cls) -> list[str]:
        """Retorna lista de valores válidos."""
        return [metodo.value for metodo in cls]


class Pago(BaseModel):
    """
    Entidad inmutable que representa un pago de alumno.
    
    Invariantes:
    - El monto debe ser mayor a cero
    - Debe tener un método de pago válido (solo efectivo o qr)
    - Debe tener un alumno asociado
    - Si está anulado, debe tener motivo y usuario que anuló
    """
    
    model_config = ConfigDict(frozen=True, strict=True)
    
    id: int = Field(..., gt=0, description="ID único del pago")
    alumno_id: int = Field(..., gt=0, description="ID del alumno que realiza el pago")
    monto_pagado: Decimal = Field(..., gt=0, decimal_places=2, description="Monto del pago")
    fecha_pago: datetime = Field(..., description="Fecha en que se realizó el pago")
    metodo_pago: MetodoPago = Field(..., description="Método de pago (efectivo o qr)")
    categoria_pago_id: int = Field(..., gt=0, description="ID de la categoría de pago")
    numero_comprobante: Optional[str] = Field(None, max_length=100, description="Número de comprobante")
    observaciones: Optional[str] = Field(None, max_length=1000, description="Observaciones adicionales")
    registrado_por: int = Field(..., gt=0, description="ID del usuario que registró el pago")
    sede_id: Optional[int] = Field(None, gt=0, description="ID de la sede")
    anulado: bool = Field(default=False, description="Indica si el pago está anulado")
    motivo_anulacion: Optional[str] = Field(None, max_length=500, description="Motivo de anulación")
    anulado_por: Optional[int] = Field(None, gt=0, description="ID del usuario que anuló")
    anulado_en: Optional[datetime] = Field(None, description="Fecha de anulación")
    creado_en: datetime = Field(default_factory=datetime.utcnow, description="Fecha de creación")
    actualizado_en: Optional[datetime] = Field(None, description="Fecha de última actualización")
    
    @field_validator('monto_pagado')
    @classmethod
    def validar_monto(cls, v: Decimal) -> Decimal:
        """Valida que el monto sea positivo."""
        if v <= 0:
            raise ValueError(f"El monto del pago debe ser mayor a cero, recibido: {v}")
        return v
    
    @field_validator('motivo_anulacion')
    @classmethod
    def validar_motivo_anulacion(cls, v: Optional[str], info) -> Optional[str]:
        """Valida que si está anulado, tenga motivo."""
        anulado = info.data.get('anulado', False)
        if anulado and not v:
            raise ValueError("Un pago anulado debe tener un motivo de anulación")
        if anulado and len(v.strip()) < 10:
            raise ValueError("El motivo de anulación debe tener al menos 10 caracteres")
        return v.strip() if v else None
    
    @field_validator('anulado_por')
    @classmethod
    def validar_anulado_por(cls, v: Optional[int], info) -> Optional[int]:
        """Valida que si está anulado, tenga usuario que anuló."""
        anulado = info.data.get('anulado', False)
        if anulado and not v:
            raise ValueError("Un pago anulado debe indicar quién lo anuló")
        return v
    
    def esta_anulado(self) -> bool:
        """Verifica si el pago está anulado."""
        return self.anulado
    
    def puede_anularse(self) -> bool:
        """Verifica si el pago puede ser anulado."""
        return not self.anulado
    
    def obtener_monto_efectivo(self) -> Decimal:
        """
        Obtiene el monto efectivo del pago.
        Si está anulado, retorna 0.
        """
        return Decimal('0.00') if self.anulado else self.monto_pagado
    
    def es_efectivo(self) -> bool:
        """Verifica si el pago fue en efectivo."""
        return self.metodo_pago == MetodoPago.EFECTIVO
    
    def es_qr(self) -> bool:
        """Verifica si el pago fue por QR."""
        return self.metodo_pago == MetodoPago.QR
    
    def to_dict(self) -> dict:
        """Convierte la entidad a diccionario."""
        return {
            'id': self.id,
            'alumno_id': self.alumno_id,
            'monto_pagado': float(self.monto_pagado),
            'fecha_pago': self.fecha_pago.isoformat(),
            'metodo_pago': self.metodo_pago.value,  # ✅ Convierte enum a string
            'categoria_pago_id': self.categoria_pago_id,
            'numero_comprobante': self.numero_comprobante,
            'observaciones': self.observaciones,
            'registrado_por': self.registrado_por,
            'sede_id': self.sede_id,
            'anulado': self.anulado,
            'motivo_anulacion': self.motivo_anulacion,
            'anulado_por': self.anulado_por,
            'anulado_en': self.anulado_en.isoformat() if self.anulado_en else None,
            'creado_en': self.creado_en.isoformat(),
            'actualizado_en': self.actualizado_en.isoformat() if self.actualizado_en else None
        }


# ==================== SCHEMAS PARA CREACIÓN/ACTUALIZACIÓN ====================

class PagoCreate(BaseModel):
    """Schema para crear un nuevo pago."""
    
    model_config = ConfigDict(strict=True)
    
    alumno_id: int = Field(..., gt=0)
    monto_pagado: Decimal = Field(..., gt=0, decimal_places=2)
    fecha_pago: datetime
    metodo_pago: MetodoPago = Field(..., description="Método de pago: efectivo o qr")
    categoria_pago_id: int = Field(..., gt=0)
    numero_comprobante: Optional[str] = Field(None, max_length=100)
    observaciones: Optional[str] = Field(None, max_length=1000)
    registrado_por: int = Field(..., gt=0)
    sede_id: Optional[int] = Field(None, gt=0)


class PagoAnular(BaseModel):
    """Schema para anular un pago."""
    
    model_config = ConfigDict(strict=True)
    
    motivo_anulacion: str = Field(..., min_length=10, max_length=500)
    anulado_por: int = Field(..., gt=0)
    
    @field_validator('motivo_anulacion')
    @classmethod
    def validar_motivo(cls, v: str) -> str:
        if not v or len(v.strip()) < 10:
            raise ValueError("El motivo de anulación debe tener al menos 10 caracteres")
        return v.strip()


class PagoResponse(BaseModel):
    """Schema de respuesta para un pago."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    alumno_id: int
    monto_pagado: Decimal
    fecha_pago: datetime
    metodo_pago: str  # ✅ String en la respuesta
    categoria_pago_id: int
    numero_comprobante: Optional[str]
    observaciones: Optional[str]
    registrado_por: int
    sede_id: Optional[int]
    anulado: bool
    motivo_anulacion: Optional[str]
    anulado_por: Optional[int]
    anulado_en: Optional[datetime]
    creado_en: datetime
    actualizado_en: Optional[datetime]
    
    @property
    def monto_efectivo(self) -> float:
        """Monto efectivo (0 si está anulado)."""
        return 0.0 if self.anulado else float(self.monto_pagado)

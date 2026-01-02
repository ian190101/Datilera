# app/kernel/domain/finanzas/egreso_entidad.py
"""
Entidad de dominio: Egreso (Gasto).
Representa un gasto o salida de dinero del centro infantil.
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field, field_validator, ConfigDict


class Egreso(BaseModel):
    """
    Entidad inmutable que representa un egreso (gasto).
    
    Invariantes:
    - El monto debe ser mayor a cero
    - La descripción no puede estar vacía (mínimo 5 caracteres)
    - Sede y categoría son obligatorios
    - Si está anulado, debe tener motivo y usuario que anuló
    """
    
    model_config = ConfigDict(frozen=True, strict=True)
    
    id: int = Field(..., gt=0, description="ID único del egreso")
    sede_id: int = Field(..., gt=0, description="ID de la sede donde se registra el egreso")
    monto: Decimal = Field(..., gt=0, decimal_places=2, description="Monto del egreso")
    categoria_egreso_id: int = Field(..., gt=0, description="ID de la categoría del egreso")
    descripcion: str = Field(..., min_length=5, max_length=500, description="Descripción del egreso")
    fecha_egreso: datetime = Field(..., description="Fecha en que se realizó el egreso")
    numero_comprobante: Optional[str] = Field(None, max_length=100, description="Número de comprobante")
    observaciones: Optional[str] = Field(None, max_length=1000, description="Observaciones adicionales")
    registrado_por: int = Field(..., gt=0, description="ID del usuario que registró el egreso")
    anulado: bool = Field(default=False, description="Indica si el egreso está anulado")
    motivo_anulacion: Optional[str] = Field(None, max_length=500, description="Motivo de anulación")
    anulado_por: Optional[int] = Field(None, gt=0, description="ID del usuario que anuló")
    anulado_en: Optional[datetime] = Field(None, description="Fecha de anulación")
    creado_en: datetime = Field(default_factory=datetime.utcnow, description="Fecha de creación")
    actualizado_en: Optional[datetime] = Field(None, description="Fecha de última actualización")
    
    @field_validator('descripcion')
    @classmethod
    def validar_descripcion(cls, v: str) -> str:
        """Valida que la descripción no sea solo espacios."""
        if not v or len(v.strip()) < 5:
            raise ValueError("La descripción debe tener al menos 5 caracteres válidos")
        return v.strip()
    
    @field_validator('monto')
    @classmethod
    def validar_monto(cls, v: Decimal) -> Decimal:
        """Valida que el monto sea positivo."""
        if v <= 0:
            raise ValueError(f"El monto del egreso debe ser mayor a cero, recibido: {v}")
        return v
    
    @field_validator('motivo_anulacion')
    @classmethod
    def validar_motivo_anulacion(cls, v: Optional[str], info) -> Optional[str]:
        """Valida que si está anulado, tenga motivo."""
        anulado = info.data.get('anulado', False)
        if anulado and not v:
            raise ValueError("Un egreso anulado debe tener un motivo de anulación")
        if anulado and len(v.strip()) < 10:
            raise ValueError("El motivo de anulación debe tener al menos 10 caracteres")
        return v.strip() if v else None
    
    @field_validator('anulado_por')
    @classmethod
    def validar_anulado_por(cls, v: Optional[int], info) -> Optional[int]:
        """Valida que si está anulado, tenga usuario que anuló."""
        anulado = info.data.get('anulado', False)
        if anulado and not v:
            raise ValueError("Un egreso anulado debe indicar quién lo anuló")
        return v
    
    def esta_anulado(self) -> bool:
        """Verifica si el egreso está anulado."""
        return self.anulado
    
    def puede_anularse(self) -> bool:
        """Verifica si el egreso puede ser anulado."""
        return not self.anulado
    
    def obtener_monto_efectivo(self) -> Decimal:
        """
        Obtiene el monto efectivo del egreso.
        Si está anulado, retorna 0.
        """
        return Decimal('0.00') if self.anulado else self.monto
    
    def to_dict(self) -> dict:
        """Convierte la entidad a diccionario."""
        return {
            'id': self.id,
            'sede_id': self.sede_id,
            'monto': float(self.monto),
            'categoria_egreso_id': self.categoria_egreso_id,
            'descripcion': self.descripcion,
            'fecha_egreso': self.fecha_egreso.isoformat(),
            'numero_comprobante': self.numero_comprobante,
            'observaciones': self.observaciones,
            'registrado_por': self.registrado_por,
            'anulado': self.anulado,
            'motivo_anulacion': self.motivo_anulacion,
            'anulado_por': self.anulado_por,
            'anulado_en': self.anulado_en.isoformat() if self.anulado_en else None,
            'creado_en': self.creado_en.isoformat(),
            'actualizado_en': self.actualizado_en.isoformat() if self.actualizado_en else None
        }


# ==================== SCHEMAS PARA CREACIÓN/ACTUALIZACIÓN ====================

class EgresoCreate(BaseModel):
    """Schema para crear un nuevo egreso."""
    
    model_config = ConfigDict(strict=True)
    
    sede_id: int = Field(..., gt=0)
    monto: Decimal = Field(..., gt=0, decimal_places=2)
    categoria_egreso_id: int = Field(..., gt=0)
    descripcion: str = Field(..., min_length=5, max_length=500)
    fecha_egreso: datetime
    numero_comprobante: Optional[str] = Field(None, max_length=100)
    observaciones: Optional[str] = Field(None, max_length=1000)
    registrado_por: int = Field(..., gt=0)
    
    @field_validator('descripcion')
    @classmethod
    def validar_descripcion(cls, v: str) -> str:
        if not v or len(v.strip()) < 5:
            raise ValueError("La descripción debe tener al menos 5 caracteres válidos")
        return v.strip()


class EgresoAnular(BaseModel):
    """Schema para anular un egreso."""
    
    model_config = ConfigDict(strict=True)
    
    motivo_anulacion: str = Field(..., min_length=10, max_length=500)
    anulado_por: int = Field(..., gt=0)
    
    @field_validator('motivo_anulacion')
    @classmethod
    def validar_motivo(cls, v: str) -> str:
        if not v or len(v.strip()) < 10:
            raise ValueError("El motivo de anulación debe tener al menos 10 caracteres")
        return v.strip()


class EgresoResponse(BaseModel):
    """Schema de respuesta para un egreso."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    sede_id: int
    monto: Decimal
    categoria_egreso_id: int
    descripcion: str
    fecha_egreso: datetime
    numero_comprobante: Optional[str]
    observaciones: Optional[str]
    registrado_por: int
    anulado: bool
    motivo_anulacion: Optional[str]
    anulado_por: Optional[int]
    anulado_en: Optional[datetime]
    creado_en: datetime
    actualizado_en: Optional[datetime]
    
    # Campos calculados
    @property
    def monto_efectivo(self) -> float:
        """Monto efectivo (0 si está anulado)."""
        return 0.0 if self.anulado else float(self.monto)

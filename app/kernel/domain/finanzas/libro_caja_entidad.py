# app/kernel/domain/finanzas/libro_caja_entidad.py
from datetime import datetime, date
from decimal import Decimal
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

class TipoMovimiento(str, Enum):
    INGRESO = "ingreso"
    EGRESO = "egreso"

class MovimientoCaja(BaseModel):
    """
    VO de movimiento en Libro de Caja (se registra con referencia).
    Inmutable (frozen=True) para garantizar integridad histórica.
    """
    model_config = ConfigDict(frozen=True)  # Reemplaza a @dataclass(frozen=True)

    fecha: date
    tipo: TipoMovimiento
    categoria_id: Optional[int]
    
    # 'ge=0' (greater or equal) permite 0 pero no negativos.
    # decimal_places=2 ayuda a validar formato en entradas JSON/Strings.
    monto: Decimal = Field(..., ge=0, decimal_places=2)
    
    referencia: Optional[str] = None  # p.ej. "pago:123", "egreso:789"
    creado_en: datetime = Field(default_factory=datetime.utcnow)

class LibroCaja(BaseModel):
    """
    Registro de movimiento en Libro de Caja.
    """
    id: int
    sede_id: int
    fecha: date
    tipo: TipoMovimiento

    # Categorías (según tipo)
    categoria_pago_id: Optional[int] = None
    categoria_egreso_id: Optional[int] = None

    # Referencias opcionales
    pago_id: Optional[int] = None

    # Valores monetarios
    # Default 0.0 y validación para no negativos
    monto: Decimal = Field(default=Decimal("0.0"), ge=0, decimal_places=2)
    saldo_acumulado: Optional[Decimal] = None

    # Metadatos
    concepto: Optional[str] = None
    referencia: Optional[str] = None
    usuario_registro_id: int = 0
    creado_en: Optional[datetime] = Field(default_factory=datetime.utcnow)
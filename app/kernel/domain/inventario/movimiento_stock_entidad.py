# app/kernel/domain/inventario/movimiento_stock_entidad.py
from __future__ import annotations
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field

class TipoMovimiento(str, Enum):
    ENTRADA = "entrada"
    SALIDA = "salida"
    TRANSFERENCIA = "transferencia"
    AJUSTE = "ajuste"

class MovimientoStock(BaseModel):
    """
    Movimiento de stock (entrada/salida/transferencia/ajuste).
    Nota del documento: se desactivó la exigencia de evidencia/ aprobación del movimiento.
    """
    id: int
    
    # Validaciones: IDs deben ser positivos
    item_id: int = Field(..., gt=0)
    sede_id: int = Field(..., gt=0)
    
    tipo: TipoMovimiento
    
    # Validación: Cantidad mayor a 0. decimal_places ayuda a serializar JSON limpiamente.
    cantidad: Decimal = Field(..., gt=0, decimal_places=2)
    
    usuario_id: int
    fecha_movimiento: date
    motivo: Optional[str] = None
    referencia: Optional[str] = None
    
    # Se genera automáticamente al instanciar
    creado_en: datetime = Field(default_factory=datetime.utcnow)
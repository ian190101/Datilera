# app/kernel/domain/inventario/prestamo_uniforme_entidad.py
from __future__ import annotations
from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field, model_validator

class PrestamoUniforme(BaseModel):
    """
    Préstamo de uniformes a personal (no venta). Se espera devolución.
    """
    id: int
    
    # Validaciones: IDs deben ser positivos
    alumno_id: int = Field(..., gt=0)
    item_id: int = Field(..., gt=0)
    
    fecha_prestamo: date
    devuelto: bool = False
    fecha_devolucion: Optional[date] = None
    
    # Se genera automáticamente al instanciar
    creado_en: datetime = Field(default_factory=datetime.utcnow)
    actualizado_en: Optional[datetime] = None

    @model_validator(mode='after')
    def inicializar_actualizado_en(self) -> PrestamoUniforme:
        """
        Si no se especifica una fecha de actualización al crear, 
        asume la misma que la de creación.
        """
        if self.actualizado_en is None:
            self.actualizado_en = self.creado_en
        return self

    # --- Comportamiento de dominio ---

    def registrar_devolucion(self, fecha: Optional[date] = None) -> None:
        """Registra la devolución, fija la fecha y actualiza auditoría."""
        if self.devuelto:
            return
        self.devuelto = True
        self.fecha_devolucion = fecha or date.today()
        self.actualizado_en = datetime.utcnow()
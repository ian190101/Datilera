from __future__ import annotations
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator

class AlertaStock(BaseModel):
    """
    Alerta por stock bajo (generada cuando `StockSede.debajo_minimo()` es True).
    """
    id: int
    item_id: int
    sede_id: int
    mensaje: str
    resuelta: bool = False
    
    # Se genera automáticamente al instanciar si no se provee
    creado_en: datetime = Field(default_factory=datetime.utcnow)
    resuelta_en: Optional[datetime] = None

    @field_validator('mensaje')
    @classmethod
    def validar_mensaje(cls, v: str) -> str:
        """Valida que el mensaje no esté vacío y limpia espacios"""
        if not (v or "").strip():
            raise ValueError("El mensaje de la alerta es obligatorio.")
        return v.strip()

    def resolver(self) -> None:
        """Marca la alerta como resuelta y registra la fecha/hora."""
        if self.resuelta:
            return
        self.resuelta = True
        self.resuelta_en = datetime.utcnow()
# app/kernel/domain/cursosextra/costo_curso_extra_entidad.py

"""
Entidad de dominio: CostoCursoExtra
"""
from __future__ import annotations
from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator


class CostoCursoExtra(BaseModel):
    """
    Entidad **CostoCursoExtra**.
    
    Representa un gasto/costo incurrido en un curso extra.
    Cada costo pertenece a una categoría definida previamente.
    
    Reglas:
    - Cada costo debe asociarse a una categoría
    - Los costos son editables hasta el cierre del período
    - El monto debe ser positivo
    """
    id: int
    curso_extra_id: int
    categoria_costo_id: int
    
    # Información del costo
    descripcion: Optional[str] = None
    monto: Decimal
    fecha_gasto: datetime = Field(default_factory=datetime.utcnow)
    
    # Comprobante (opcional - futuro módulo)
    comprobante_url: Optional[str] = None
    
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        from_attributes=True,
    )
    
    @field_validator("monto")
    @classmethod
    def _monto_valido(cls, v: Decimal) -> Decimal:
        """Valida que el monto sea positivo."""
        if v <= Decimal("0"):
            raise ValueError("El monto del costo debe ser mayor a 0.")
        return v
    
    @field_validator("descripcion")
    @classmethod
    def _descripcion_valida(cls, v: Optional[str]) -> Optional[str]:
        """Valida longitud de descripción."""
        if v and len(v) > 1000:
            raise ValueError("La descripción no puede superar 1000 caracteres.")
        return v
    
    # --- Comportamiento ---
    
    def tiene_comprobante(self) -> bool:
        """Verifica si tiene comprobante adjunto."""
        return self.comprobante_url is not None
    
    def actualizar_monto(self, nuevo_monto: Decimal) -> None:
        """Actualiza el monto del costo."""
        if nuevo_monto <= Decimal("0"):
            raise ValueError("El monto debe ser mayor a 0.")
        self.monto = nuevo_monto
    
    def actualizar_descripcion(self, nueva_descripcion: str) -> None:
        """Actualiza la descripción del costo."""
        if len(nueva_descripcion) > 1000:
            raise ValueError("La descripción no puede superar 1000 caracteres.")
        self.descripcion = nueva_descripcion

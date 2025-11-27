# app/kernel/domain/inventario/item_entidad.py
from __future__ import annotations
from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field, field_validator, model_validator, ValidationInfo

class Item(BaseModel):
    """
    Entidad Item (producto/activo del inventario).
    - `codigo` es único (SKU/código interno). La generación real del código puede
      resolverse en la capa de aplicación/infraestructura; aquí se valida su presencia.
    - `unidad_medida`: 'unidad', 'kg', 'lt', etc. (catálogo configurable fuera del dominio).
    """
    id: int
    
    # Validación: ID positivo
    categoria_id: int = Field(..., gt=0)
    
    codigo: str
    nombre: str
    
    # Validación: Precio no negativo, precisión monetaria
    precio_unitario: Decimal = Field(..., ge=0, decimal_places=2)
    
    unidad_medida: str = "unidad"
    descripcion: Optional[str] = None
    activo: bool = True
    
    # Se genera automáticamente
    creado_en: datetime = Field(default_factory=datetime.utcnow)
    actualizado_en: Optional[datetime] = None

    @field_validator('codigo', 'nombre')
    @classmethod
    def validar_textos_obligatorios(cls, v: str, info: ValidationInfo) -> str:
        """Valida que código y nombre no estén vacíos."""
        if not (v or "").strip():
            campo = "código" if info.field_name == "codigo" else "nombre"
            raise ValueError(f"El {campo} del ítem es obligatorio.")
        return v.strip()

    @model_validator(mode='after')
    def inicializar_actualizado_en(self) -> Item:
        """
        Replica la lógica: self.actualizado_en = self.actualizado_en or self.creado_en
        Si no viene una fecha de actualización, asume la de creación.
        """
        if self.actualizado_en is None:
            self.actualizado_en = self.creado_en
        return self

    # --- Reglas de negocio sencillas ---

    def cambiar_precio(self, nuevo_precio: Decimal) -> None:
        """Actualiza el precio y la fecha de modificación."""
        # Convertimos a Decimal por seguridad si entra float/int
        precio_decimal = Decimal(nuevo_precio)
        if precio_decimal < 0:
            raise ValueError("El precio unitario no puede ser negativo.")
        
        self.precio_unitario = precio_decimal
        self.actualizado_en = datetime.utcnow()

    def activar(self) -> None:
        if not self.activo:
            self.activo = True
            self.actualizado_en = datetime.utcnow()

    def desactivar(self) -> None:
        if self.activo:
            self.activo = False
            self.actualizado_en = datetime.utcnow()
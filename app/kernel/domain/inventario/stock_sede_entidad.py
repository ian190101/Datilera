# app/kernel/domain/inventario/stock_sede_entidad.py
from __future__ import annotations
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field

class StockSede(BaseModel):
    """
    Stock disponible por ítem y sede.
    - `stock_minimo`: umbral para generar alertas (la generación/dispatch se hace fuera).
    """
    id: int
    
    # Validaciones: IDs deben ser positivos
    item_id: int = Field(..., gt=0)
    sede_id: int = Field(..., gt=0)
    
    # Validaciones: Cantidades no negativas
    # decimal_places ayuda a estandarizar la precisión en serialización JSON
    cantidad_disponible: Decimal = Field(..., ge=0, decimal_places=2)
    stock_minimo: Decimal = Field(..., ge=0, decimal_places=2)
    
    # Se genera/actualiza automáticamente
    actualizado_en: datetime = Field(default_factory=datetime.utcnow)

    # --- Operaciones de stock ---

    def aumentar(self, cantidad: Decimal) -> None:
        """Aumenta stock y actualiza timestamp."""
        cant = Decimal(cantidad)
        if cant <= 0:
            raise ValueError("La cantidad a aumentar debe ser > 0.")
        
        self.cantidad_disponible += cant
        self.actualizado_en = datetime.utcnow()

    def disminuir(self, cantidad: Decimal) -> None:
        """Disminuye stock validando disponibilidad y actualiza timestamp."""
        cant = Decimal(cantidad)
        if cant <= 0:
            raise ValueError("La cantidad a disminuir debe ser > 0.")
        
        nueva = self.cantidad_disponible - cant
        
        if nueva < 0:
            raise ValueError("No hay stock suficiente.")
            
        self.cantidad_disponible = nueva
        self.actualizado_en = datetime.utcnow()

    def debajo_minimo(self) -> bool:
        """Verifica si es necesario reabastecer."""
        return self.cantidad_disponible <= self.stock_minimo
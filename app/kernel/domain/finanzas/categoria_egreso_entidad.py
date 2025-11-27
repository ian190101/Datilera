# app/kernel/domain/finanzas/categoria_egreso_entidad.py
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator

class CategoriaEgreso(BaseModel):
    """
    Categoría de egreso por sede (sueldos, alquiler, servicios, insumos, mantenimiento, etc.)
    
    Historias:
    - Categorías dinámicas por sede para clasificar egresos en libro de caja
    - Usadas en reportes financieros y arqueos mensuales
    """
    id: int
    sede_id: int
    nombre: str
    descripcion: Optional[str] = None
    activa: bool = True
    # Usamos default_factory para generar la fecha al instanciar si no se provee una
    creado_en: datetime = Field(default_factory=datetime.utcnow)

    @field_validator('nombre')
    @classmethod
    def validar_nombre(cls, v: str) -> str:
        """Valida que el nombre no esté vacío o sea solo espacios"""
        if not (v or "").strip():
            raise ValueError("El nombre de la categoría de egreso es obligatorio.")
        return v

    def desactivar(self) -> None:
        """Desactiva la categoría (no se puede eliminar para mantener historial)"""
        self.activa = False

    def activar(self) -> None:
        """Reactiva la categoría"""
        self.activa = True
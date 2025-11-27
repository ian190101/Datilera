# app/kernel/domain/cursosextra/ingreso_curso_extra_entidad.py

"""
Entidad de dominio: IngresoCursoExtra
"""
from __future__ import annotations
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, field_validator


class IngresoCursoExtra(BaseModel):
    """
    Entidad **IngresoCursoExtra**.
    
    Consolida los ingresos totales de un curso extra (suma de pagos).
    Facilita el cálculo de balance: ganancia = ingresos - gastos.
    Se actualiza automáticamente con cada pago o gasto registrado.
    
    Reglas:
    - Un curso tiene un único registro de ingresos
    - Se recalcula automáticamente al registrar pagos/gastos
    - La distribución de ganancias se basa en el porcentaje del curso
    """
    id: int
    curso_extra_id: int
    
    # Montos consolidados
    total_ingresos: Decimal = Decimal("0.00")
    total_gastos: Decimal = Decimal("0.00")
    ganancia_bruta: Decimal = Decimal("0.00")
    
    # Distribución de ganancias
    ganancia_institucion: Decimal = Decimal("0.00")
    ganancia_instructor: Decimal = Decimal("0.00")
    
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        from_attributes=True,
    )
    
    @field_validator("total_ingresos", "total_gastos", "ganancia_bruta", 
                     "ganancia_institucion", "ganancia_instructor")
    @classmethod
    def _montos_no_negativos(cls, v: Decimal) -> Decimal:
        """Valida que los montos no sean negativos."""
        if v < Decimal("0"):
            raise ValueError("Los montos no pueden ser negativos.")
        return v
    
    # --- Comportamiento ---
    
    def actualizar_ingresos(self, total_ingresos: Decimal) -> None:
        """Actualiza el total de ingresos."""
        if total_ingresos < Decimal("0"):
            raise ValueError("El total de ingresos no puede ser negativo.")
        self.total_ingresos = total_ingresos
    
    def actualizar_gastos(self, total_gastos: Decimal) -> None:
        """Actualiza el total de gastos."""
        if total_gastos < Decimal("0"):
            raise ValueError("El total de gastos no puede ser negativo.")
        self.total_gastos = total_gastos
    
    def recalcular_ganancias(self, porcentaje_institucion: Decimal) -> None:
        """
        Recalcula todas las ganancias basándose en el porcentaje de la institución.
        
        Args:
            porcentaje_institucion: Porcentaje (0-100) que corresponde a la institución
        """
        if porcentaje_institucion < Decimal("0") or porcentaje_institucion > Decimal("100"):
            raise ValueError("El porcentaje debe estar entre 0 y 100.")
        
        # Ganancia bruta = ingresos - gastos
        self.ganancia_bruta = self.total_ingresos - self.total_gastos
        
        # Distribución según porcentaje
        self.ganancia_institucion = (
            self.ganancia_bruta * porcentaje_institucion / Decimal("100")
        )
        self.ganancia_instructor = self.ganancia_bruta - self.ganancia_institucion
    
    def tiene_ganancias(self) -> bool:
        """Verifica si hay ganancias positivas."""
        return self.ganancia_bruta > Decimal("0")
    
    def tiene_perdidas(self) -> bool:
        """Verifica si hay pérdidas."""
        return self.ganancia_bruta < Decimal("0")
    
    def esta_equilibrado(self) -> bool:
        """Verifica si está en punto de equilibrio."""
        return self.ganancia_bruta == Decimal("0")
    
    def obtener_margen_porcentual(self) -> Decimal:
        """Calcula el margen de ganancia porcentual."""
        if self.total_ingresos == Decimal("0"):
            return Decimal("0")
        return (self.ganancia_bruta / self.total_ingresos) * Decimal("100")

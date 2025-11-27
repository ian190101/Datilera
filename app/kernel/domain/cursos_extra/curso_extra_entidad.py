# app/kernel/domain/cursosextra/curso_extra_entidad.py

"""
Entidad de dominio: CursoExtra
"""
from __future__ import annotations
from datetime import date
from decimal import Decimal
from enum import Enum
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator


class CursoExtra(BaseModel):
    """
    Entidad **CursoExtra**.
    
    Representa un curso extracurricular con precios diferenciados,
    límite de cupos y reparto de ganancias entre institución e instructor.
    
    Reglas de negocio:
    - Precios diferenciados: internos (alumnos del centro) vs externos
    - Cupos limitados con control en tiempo real
    - Distribución de ganancias configurable por curso
    - Puede tener múltiples ediciones (misma gestión, diferentes fechas)
    """
    id: int
    sede_id: int
    nombre: str
    descripcion: Optional[str] = None
    instructor: str
    gestion: int
    
    # Fechas
    fecha_inicio: date
    fecha_fin: Optional[date] = None  # Opcional para cursos permanentes
    
    # Control de cupos
    cupo_maximo: int
    inscritos_actuales: int = 0
    
    # Precios diferenciados
    precio_interno: Decimal
    precio_externo: Decimal
    
    # Reparto de ganancias
    porcentaje_institucion: Decimal = Decimal("50.00")
    
    # Estado
    activo: bool = True
    
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        from_attributes=True,
    )
    
    @field_validator("nombre")
    @classmethod
    def _nombre_valido(cls, v: str) -> str:
        """Valida nombre obligatorio."""
        nombre = (v or "").strip()
        if not nombre:
            raise ValueError("El nombre del curso es obligatorio.")
        if len(nombre) > 120:
            raise ValueError("El nombre no puede superar 120 caracteres.")
        return nombre
    
    @field_validator("instructor")
    @classmethod
    def _instructor_valido(cls, v: str) -> str:
        """Valida instructor obligatorio."""
        instructor = (v or "").strip()
        if not instructor:
            raise ValueError("El instructor es obligatorio.")
        if len(instructor) > 120:
            raise ValueError("El nombre del instructor no puede superar 120 caracteres.")
        return instructor
    
    @field_validator("cupo_maximo")
    @classmethod
    def _cupo_valido(cls, v: int) -> int:
        """Valida cupo máximo positivo."""
        if v <= 0:
            raise ValueError("El cupo máximo debe ser mayor a 0.")
        return v
    
    @field_validator("porcentaje_institucion")
    @classmethod
    def _porcentaje_valido(cls, v: Decimal) -> Decimal:
        """Valida porcentaje entre 0 y 100."""
        if v < Decimal("0") or v > Decimal("100"):
            raise ValueError("El porcentaje debe estar entre 0 y 100.")
        return v
    
    # --- Comportamiento ---
    
    def tiene_cupos_disponibles(self) -> bool:
        """Verifica si hay cupos disponibles."""
        return self.inscritos_actuales < self.cupo_maximo
    
    def incrementar_inscritos(self) -> None:
        """Incrementa el contador de inscritos."""
        if not self.tiene_cupos_disponibles():
            raise ValueError(f"El curso '{self.nombre}' no tiene cupos disponibles.")
        self.inscritos_actuales += 1
    
    def decrementar_inscritos(self) -> None:
        """Decrementa el contador de inscritos."""
        if self.inscritos_actuales > 0:
            self.inscritos_actuales -= 1
    
    def calcular_precio_para(self, es_alumno_interno: bool) -> Decimal:
        """Retorna el precio según el tipo de alumno."""
        return self.precio_interno if es_alumno_interno else self.precio_externo
    
    def esta_activo(self) -> bool:
        """Verifica si el curso está activo."""
        return self.activo
    
    def activar(self) -> None:
        """Activa el curso."""
        self.activo = True
    
    def desactivar(self) -> None:
        """Desactiva el curso."""
        self.activo = False

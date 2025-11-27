# app/kernel/domain/cursosextra/alumno_externo_entidad.py

"""
Entidad de dominio: AlumnoExterno
"""
from __future__ import annotations
from datetime import date
from typing import Optional
from pydantic import BaseModel, ConfigDict, field_validator


class AlumnoExterno(BaseModel):
    """
    Entidad **AlumnoExterno**.
    
    Representa un niño externo (no inscrito al centro) que participa
    solo en cursos extra.
    
    Reglas:
    - Datos básicos del niño + contacto del tutor
    - Un alumno externo puede inscribirse en múltiples cursos de la misma sede
    """
    id: int
    sede_id: int
    nombre_completo: str
    fecha_nacimiento: Optional[date] = None
    edad_anios: Optional[int] = None
    
    # Datos del tutor responsable
    tutor_nombre: str
    tutor_celular: str
    tutor_email: Optional[str] = None
    
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        from_attributes=True,
    )
    
    @field_validator("nombre_completo")
    @classmethod
    def _nombre_valido(cls, v: str) -> str:
        """Valida nombre obligatorio."""
        nombre = (v or "").strip()
        if not nombre:
            raise ValueError("El nombre completo del niño es obligatorio.")
        if len(nombre) > 200:
            raise ValueError("El nombre no puede superar 200 caracteres.")
        return nombre
    
    @field_validator("tutor_nombre")
    @classmethod
    def _tutor_nombre_valido(cls, v: str) -> str:
        """Valida nombre del tutor obligatorio."""
        tutor = (v or "").strip()
        if not tutor:
            raise ValueError("El nombre del tutor es obligatorio.")
        if len(tutor) > 200:
            raise ValueError("El nombre del tutor no puede superar 200 caracteres.")
        return tutor
    
    @field_validator("tutor_celular")
    @classmethod
    def _celular_valido(cls, v: str) -> str:
        """Valida celular obligatorio."""
        celular = (v or "").strip()
        if not celular:
            raise ValueError("El celular del tutor es obligatorio.")
        if len(celular) > 15:
            raise ValueError("El celular no puede superar 15 caracteres.")
        return celular
    
    # --- Comportamiento ---
    
    def calcular_edad(self) -> Optional[int]:
        """Calcula la edad actual del niño."""
        if not self.fecha_nacimiento:
            return self.edad_anios
        
        hoy = date.today()
        edad = hoy.year - self.fecha_nacimiento.year
        
        # Ajustar si aún no cumplió años este año
        if (hoy.month, hoy.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day):
            edad -= 1
        
        return edad

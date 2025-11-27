# app/domain/entities/alumnos/autorizacion_retiro_entidad.py

from pydantic import BaseModel, ConfigDict, field_validator
from typing import Optional
from datetime import datetime


class AutorizacionRetiroEntidad(BaseModel):
    """Entidad de dominio para autorizaciones de retiro"""
    
    model_config = ConfigDict(
        from_attributes=True,
        validate_assignment=True
    )

    id: Optional[int] = None
    alumno_id: int
    
    # Persona autorizada
    nombres: str
    apellidos: str
    ci_numero: str
    telefono: str
    relacion: str  # tio, primo, abuelo, amigo_familia, etc.
    
    # Estado
    activo: bool = True
    
    # Auditoría
    creado_en: Optional[datetime] = None
    autorizado_por_id: Optional[int] = None

    @field_validator('ci_numero')
    @classmethod
    def validar_ci(cls, v: str) -> str:
        if not v or len(v.strip()) < 5:
            raise ValueError("El CI debe tener al menos 5 caracteres")
        return v.strip()

    @field_validator('telefono')
    @classmethod
    def validar_telefono(cls, v: str) -> str:
        if not v or len(v.strip()) < 7:
            raise ValueError("El teléfono debe tener al menos 7 dígitos")
        return v.strip()

    @property
    def nombre_completo(self) -> str:
        """Retorna el nombre completo de la persona autorizada"""
        return f"{self.nombres} {self.apellidos}"

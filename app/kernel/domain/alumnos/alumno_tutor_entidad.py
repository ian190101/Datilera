# app/domain/entities/alumnos/alumno_tutor_entidad.py

from pydantic import BaseModel, ConfigDict, field_validator
from typing import Optional
from datetime import datetime


class AlumnoTutorEntidad(BaseModel):
    """Entidad de dominio para relación Alumno-Tutor"""
    
    model_config = ConfigDict(
        from_attributes=True,
        validate_assignment=True
    )

    id: Optional[int] = None
    alumno_id: int
    tutor_id: int
    relacion: str  # padre, madre, abuelo, tio, tutor_legal, etc.
    es_principal: bool = False
    vive_con_alumno: bool = False
    autorizacion_retiro: bool = True
    prioridad_contacto: int = 1  # 1 = primero en ser contactado
    
    # Auditoría
    creado_en: Optional[datetime] = None
    actualizado_en: Optional[datetime] = None

    @field_validator('relacion')
    @classmethod
    def validar_relacion(cls, v: str) -> str:
        relaciones_validas = [
            'padre', 'madre', 'abuelo', 'abuela', 
            'tio', 'tia', 'hermano', 'hermana',
            'tutor_legal', 'otro'
        ]
        if v.lower() not in relaciones_validas:
            raise ValueError(f"Relación debe ser una de: {', '.join(relaciones_validas)}")
        return v.lower()

    @field_validator('prioridad_contacto')
    @classmethod
    def validar_prioridad(cls, v: int) -> int:
        if v < 1 or v > 10:
            raise ValueError("La prioridad debe estar entre 1 y 10")
        return v

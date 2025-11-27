# app/domain/entities/alumnos/alumno_paralelo_entidad.py

from pydantic import BaseModel, ConfigDict, field_validator
from typing import Optional
from datetime import datetime


class AlumnoParaleloEntidad(BaseModel):
    """Entidad de dominio para asignación de alumno a paralelo"""
    
    model_config = ConfigDict(
        from_attributes=True,
        validate_assignment=True
    )

    id: Optional[int] = None
    alumno_id: int
    paralelo_id: int
    
    # Auditoría
    creado_en: Optional[datetime] = None
    asignado_por_id: Optional[int] = None

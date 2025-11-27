# app/domain/entities/alumnos/consentimiento_entidad.py

from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class ConsentimientoEntidad(BaseModel):
    """Entidad de dominio para consentimientos del alumno"""
    
    model_config = ConfigDict(
        from_attributes=True,
        validate_assignment=True
    )

    id: Optional[int] = None
    alumno_id: int
    
    # Consentimientos
    uso_imagen: bool = False
    actividades_externas: bool = False
    atencion_medica_emergencia: bool = True  # Generalmente requerido
    transporte_autorizado: bool = False
    publicacion_trabajos: bool = False
    
    # Auditoría
    creado_en: Optional[datetime] = None
    actualizado_en: Optional[datetime] = None
    actualizado_por_id: Optional[int] = None

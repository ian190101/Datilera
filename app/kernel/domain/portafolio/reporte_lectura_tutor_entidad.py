# app/kernel/domain/portafolio/lectura_tutor_entidad.py
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class LecturaTutor(BaseModel):
    """
    Entidad de dominio para la confirmación de lectura de un tutor.
    Mapea a app.infrastructure.db.models.portafolio.ReporteLecturaTutor.
    """
    
    # 1. Configuración moderna
    model_config = ConfigDict(from_attributes=True)

    id: int
    
    # 2. CORRECCIÓN CRÍTICA: Debe coincidir con el nombre en el modelo de BD
    reporte_diario_id: int 
    
    tutor_id: int
    leido: bool
    leido_en: datetime
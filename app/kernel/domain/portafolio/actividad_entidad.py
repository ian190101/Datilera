# app/kernel/domain/portafolio/actividad_portafolio_entidad.py
from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class ActividadPortafolio(BaseModel):
    """
    Entidad de dominio para una actividad del portafolio.
    Mapea a app.infrastructure.db.models.portafolio.Actividad.
    """
    
    # Configuración moderna Pydantic V2
    model_config = ConfigDict(from_attributes=True)

    id: int
    alumno_id: Optional[int] = None
    grupo_id: Optional[int] = None
    
    # FALTABA: Es obligatorio en tu modelo DB
    profesora_id: int
    
    # CORRECCIÓN: En tu DB se llama 'fecha_actividad', no 'fecha'
    fecha_actividad: date
    
    # Ajusté el max_length a 150 para coincidir con tu String(150) de la BD
    titulo: str = Field(max_length=150)
    
    descripcion: Optional[str] = None
    
    # ELIMINADO: 'tipo' no existe en tu tabla de actividades.
    
    # SUGERENCIA: Campos de auditoría útiles para el frontend
    creado_en: Optional[datetime] = None
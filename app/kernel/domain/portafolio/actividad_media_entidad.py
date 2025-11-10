# app/kernel/domain/portafolio/actividad_media_entidad.py
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional


class TipoMedia(str, Enum):
    IMAGEN = "imagen"
    VIDEO = "video"
    AUDIO = "audio"
    DOCUMENTO = "documento"


@dataclass
class ActividadMedia:
    """
    Media asociada a una actividad.
    - `tipo`: imagen | video | audio | documento
    - `url` obligatoria; `titulo` opcional (≤120)
    """
    id: int
    actividad_id: int
    tipo: TipoMedia
    url: str
    titulo: Optional[str] = None
    creado_en: datetime = None

    def __post_init__(self):
        if not (self.url or "").strip():
            raise ValueError("La URL del recurso es obligatoria.")
        if self.titulo is not None and len(self.titulo) > 120:
            raise ValueError("El título de la media no puede exceder 120 caracteres.")
        self.creado_en = self.creado_en or datetime.utcnow()
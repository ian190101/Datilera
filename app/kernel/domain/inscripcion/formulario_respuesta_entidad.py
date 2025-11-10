# app/kernel/domain/inscripcion/formulario_respuesta_entidad.py
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime


@dataclass
class FormularioRespuesta:
    """
    Respuesta granular (campo/valor) de un formulario de inscripción.
    Se usa para el formulario largo dividido en secciones/pasos.
    """
    id: int
    formulario_id: int
    campo: str
    valor: str
    creado_en: datetime = None

    def __post_init__(self):
        if not (self.campo or "").strip():
            raise ValueError("El nombre del campo es obligatorio.")
        if not (self.valor or "").strip():
            raise ValueError("El valor del campo es obligatorio.")
        self.creado_en = self.creado_en or datetime.utcnow()
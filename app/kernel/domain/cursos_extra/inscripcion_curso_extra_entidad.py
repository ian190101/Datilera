# app/kernel/domain/cursos_extra/inscripcion_curso_extra_entidad.py
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, date
from enum import Enum
from typing import Optional


class TipoParticipanteCurso(str, Enum):
    INSCRITO_CENTRO = 'inscrito_centro'
    EXTERNO = 'externo'


class InscripcionDuplicadaError(Exception):
    """Intento de inscribir dos veces al mismo niño para el mismo curso."""


@dataclass(frozen=True)
class DatosExterno:
    nombre_nino: str
    tutor_nombre: str
    tutor_celular: str  # validación de formato en la capa de aplicación
    edad_meses: int     # edad en meses (ej: 1 año 6 meses -> 18)

    def __post_init__(self):
        if not (self.nombre_nino and self.tutor_nombre and self.tutor_celular):
            raise ValueError('Datos de externo incompletos.')
        if self.edad_meses < 0:
            raise ValueError('La edad en meses no puede ser negativa.')


class InscripcionCursoExtra:
    """Entidad InscripcionCursoExtra.

    - Puede ser de un niño INSCRITO (nino_id) o un EXTERNO (DatosExterno).
    - Registra la fecha de ingreso al curso.
    - La validación de cupo se hace en CursoExtra.registrar_inscripcion().
    """

    def __init__(
        self,
        id: int,
        curso_id: int,
        tipo_participante: TipoParticipanteCurso,
        fecha_ingreso: date,
        nino_id: Optional[int] = None,
        datos_externo: Optional[DatosExterno] = None,
        creado_en: Optional[datetime] = None,
    ):
        if tipo_participante == TipoParticipanteCurso.INSCRITO_CENTRO and not nino_id:
            raise ValueError('Se requiere nino_id para INSCRITO_CENTRO.')
        if tipo_participante == TipoParticipanteCurso.EXTERNO and not datos_externo:
            raise ValueError('Se requieren datos_externo para EXTERNO.')

        self.id = id
        self.curso_id = curso_id
        self.tipo_participante = tipo_participante
        self.fecha_ingreso = fecha_ingreso
        self.nino_id = nino_id
        self.datos_externo = datos_externo
        self.creado_en = creado_en or datetime.utcnow()
"""
Repositorios para el módulo de Cursos Extra.
"""
from .curso_extra_repo import CursoExtraRepository
from .inscripciones_curso_extra_repo import InscripcionCursoExtraRepository
from .alumno_externo_repo import AlumnoExternoRepository
from .balance_curso_extra_repo import BalanceCursoExtraRepository
from .pago_curso_extra_repo import PagoCursoExtraRepository
from .costo_curso_extra_repo import CostoCursoExtraRepository
from .categoria_costo_repo import CategoriaCostoCursoExtraRepository
from .ingreso_curso_extra_repo import IngresoCursoExtraRepository

__all__ = [
    "CursoExtraRepository",
    "InscripcionCursoExtraRepository",
    "AlumnoExternoRepository",
    "BalanceCursoExtraRepository",
    "PagoCursoExtraRepository",
    "CostoCursoExtraRepository",
    "CategoriaCostoCursoExtraRepository",
    "IngresoCursoExtraRepository",
]

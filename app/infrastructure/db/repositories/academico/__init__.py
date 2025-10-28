# app/infrastructure/db/repositories/academico/__init__.py
from .grupos_repo import GruposRepository
from .paralelos_repo import ParalelosRepository
from .paralelos_profesoras_repo import ParalelosProfesorasRepository
from .horarios_repo import HorariosRepository
from .horarios_paralelos_repo import HorariosParalelosRepository

__all__ = [
    "GruposRepository", "ParalelosRepository", "ParalelosProfesorasRepository",
    "HorariosRepository", "HorariosParalelosRepository",
]

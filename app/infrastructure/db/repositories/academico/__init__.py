# app/infrastructure/db/repositories/academico/__init__.py
from .grupos_repo import GruposRepository
from .paralelos_repo import ParalelosRepository
from .paralelos_profesoras_repo import ParalelosProfesorasRepository

__all__ = [
    "GruposRepository", "ParalelosRepository", "ParalelosProfesorasRepository",
]

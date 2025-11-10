# app/kernel/domain/cursos_extra/costo_curso_extra_entidad.py
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from decimal import Decimal
from typing import Optional


class CategoriaCosto(str, Enum):
    """Categorías de costo típicas; pueden ampliarse en catálogos por sede/curso."""
    MATERIALES = 'materiales'
    HORAS_HOMBRE = 'horas_hombre'
    ALQUILER = 'alquiler'
    PUBLICIDAD = 'publicidad'
    OTROS = 'otros'


@dataclass
class CostoCursoExtra:
    """Entidad CostoCursoExtra.

    - Costo imputado a un curso, con categoría definida por el curso/sede.
    - Soporta archivo de respaldo opcional (imagen/PDF).
    """

    id: int
    curso_id: int
    categoria: CategoriaCosto
    monto: Decimal
    descripcion: Optional[str] = None
    respaldo_ruta: Optional[str] = None
    creado_por_usuario_id: Optional[int] = None
    creado_en: datetime = None

    def __post_init__(self):
        if Decimal(self.monto) < 0:
            raise ValueError('El monto del costo no puede ser negativo.')
        self.creado_en = self.creado_en or datetime.utcnow()
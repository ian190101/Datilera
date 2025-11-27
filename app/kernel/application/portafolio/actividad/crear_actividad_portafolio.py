from __future__ import annotations

from datetime import date
from typing import Optional

from pydantic import BaseModel, Field

from app.kernel.domain.portafolio import (
    ActividadPortafolio,
    AbstractActividadesRepository,
)


class CrearActividadPortafolioIn(BaseModel):
    alumno_id: Optional[int] = Field(default=None, gt=0)
    grupo_id: Optional[int] = Field(default=None, gt=0)
    fecha: date
    titulo: str = Field(max_length=120)
    descripcion: Optional[str] = None
    tipo: str = Field(max_length=40)


class CrearActividadPortafolioOut(BaseModel):
    actividad: ActividadPortafolio


class CrearActividadPortafolioCU:
    def __init__(self, actividades_repo: AbstractActividadesRepository) -> None:
        self._actividades_repo = actividades_repo

    async def __call__(
        self,
        data: CrearActividadPortafolioIn,
    ) -> CrearActividadPortafolioOut:
        actividad = await self._actividades_repo.crear(
            alumno_id=data.alumno_id,
            grupo_id=data.grupo_id,
            fecha=data.fecha,
            titulo=data.titulo,
            descripcion=data.descripcion,
            tipo=data.tipo,
        )
        return CrearActividadPortafolioOut(actividad=actividad)

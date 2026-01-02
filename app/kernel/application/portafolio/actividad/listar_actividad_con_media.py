# app/kernel/application/portafolio/actividad/listar_actividad_con_media.py
from __future__ import annotations

from typing import List

from pydantic import BaseModel, Field

from app.kernel.domain.portafolio import (
    ActividadPortafolio,
    ArchivoMediaPortafolio,
    AbstractActividadesRepository,
    AbstractActividadMediaRepository,
    ActividadNoEncontradaError,
)


class ListarActividadConMediaIn(BaseModel):
    actividad_id: int = Field(gt=0)


class ListarActividadConMediaOut(BaseModel):
    actividad: ActividadPortafolio
    media: List[ArchivoMediaPortafolio]

    # ¡¡OBLIGATORIO para que FastAPI serialice objetos ORM y listas de ORM!!
    model_config = {"from_attributes": True}


class ListarActividadConMediaCU:
    def __init__(
        self,
        actividades_repo: AbstractActividadesRepository,
        media_repo: AbstractActividadMediaRepository,
    ) -> None:
        self._actividades_repo = actividades_repo
        self._media_repo = media_repo

    # CAMBIADO: de __call__ → execute
    async def execute(
        self,
        data: ListarActividadConMediaIn,
    ) -> ListarActividadConMediaOut:
        actividad = await self._actividades_repo.obtener_por_id(data.actividad_id)
        if actividad is None:
            raise ActividadNoEncontradaError(actividad_id=data.actividad_id)

        media = await self._media_repo.listar_por_actividad(data.actividad_id)
        return ListarActividadConMediaOut(actividad=actividad, media=media)
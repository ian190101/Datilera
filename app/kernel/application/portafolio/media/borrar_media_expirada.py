from __future__ import annotations

from datetime import datetime
from typing import List

from pydantic import BaseModel

from app.kernel.domain.portafolio import (
    ArchivoMediaPortafolio,
    AbstractActividadMediaRepository,
    AbstractStorageService,
    EstadoMedia,
)


class BorrarMediaExpiradaIn(BaseModel):
    ahora: datetime


class BorrarMediaExpiradaOut(BaseModel):
    borrados_ids: List[int]


class BorrarMediaExpiradaCU:
    def __init__(
        self,
        media_repo: AbstractActividadMediaRepository,
        storage_service: AbstractStorageService,
    ) -> None:
        self._media_repo = media_repo
        self._storage_service = storage_service

    async def __call__(self, data: BorrarMediaExpiradaIn) -> BorrarMediaExpiradaOut:
        vencidos: List[ArchivoMediaPortafolio] = await self._media_repo.listar_para_borrado(
            ahora=data.ahora
        )

        ids_borrados: List[int] = []

        for media in vencidos:
            path = media.url_marcada or media.url_original
            await self._storage_service.eliminar_archivo(path)

            await self._media_repo.actualizar_estado_y_urls(
                media_id=media.id,
                estado=EstadoMedia.ELIMINADO.value,
                url_marcada=media.url_marcada,
            )
            ids_borrados.append(media.id)

        return BorrarMediaExpiradaOut(borrados_ids=ids_borrados)

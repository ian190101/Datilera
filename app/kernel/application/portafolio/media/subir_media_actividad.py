from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field

from app.kernel.domain.portafolio import (
    ArchivoMediaPortafolio,
    AbstractActividadMediaRepository,
    AbstractActividadesRepository,
    ActividadNoEncontradaError,
    MediaNoDisponibleError,
)
from app.kernel.domain.portafolio.actividad_media_entidad import TipoMedia


MAX_FOTOS_POR_ACTIVIDAD = 5
MAX_VIDEOS_POR_ACTIVIDAD = 3


class SubirMediaActividadIn(BaseModel):
    actividad_id: int = Field(gt=0)
    tipo: str  # "foto" | "video"
    url_original: str
    nombre_archivo: str
    mime: Optional[str] = None
    tamano_bytes: Optional[int] = None


class SubirMediaActividadOut(BaseModel):
    media: ArchivoMediaPortafolio


class SubirMediaActividadCU:
    def __init__(
        self,
        actividades_repo: AbstractActividadesRepository,
        media_repo: AbstractActividadMediaRepository,
    ) -> None:
        self._actividades_repo = actividades_repo
        self._media_repo = media_repo

    async def __call__(
        self,
        data: SubirMediaActividadIn,
    ) -> SubirMediaActividadOut:
        actividad = await self._actividades_repo.obtener_por_id(data.actividad_id)
        if actividad is None:
            raise ActividadNoEncontradaError(actividad_id=data.actividad_id)

        conteo = await self._media_repo.contar_por_tipo(data.actividad_id)
        tipo_normalizado = data.tipo.lower()

        if tipo_normalizado == TipoMedia.FOTO.value:
            if conteo.get(TipoMedia.FOTO.value, 0) >= MAX_FOTOS_POR_ACTIVIDAD:
                raise MediaNoDisponibleError(media_id=0)
        elif tipo_normalizado == TipoMedia.VIDEO.value:
            if conteo.get(TipoMedia.VIDEO.value, 0) >= MAX_VIDEOS_POR_ACTIVIDAD:
                raise MediaNoDisponibleError(media_id=0)
        else:
            raise MediaNoDisponibleError(media_id=0)

        media = await self._media_repo.crear(
            actividad_id=data.actividad_id,
            tipo=tipo_normalizado,
            url_original=data.url_original,
            nombre_archivo=data.nombre_archivo,
            mime=data.mime,
            tamano_bytes=data.tamano_bytes,
        )
        return SubirMediaActividadOut(media=media)

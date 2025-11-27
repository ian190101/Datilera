from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from app.kernel.domain.portafolio import (
    ArchivoMediaPortafolio,
    AbstractActividadMediaRepository,
    MediaNoEncontradaError,
    MediaExpiradaError,
    PoliticaExpiracionMedia,
    EstadoMedia,
)


class RegistrarDescargaMediaIn(BaseModel):
    media_id: int = Field(gt=0)


class RegistrarDescargaMediaOut(BaseModel):
    media: ArchivoMediaPortafolio


class RegistrarDescargaMediaCU:
    def __init__(
        self,
        media_repo: AbstractActividadMediaRepository,
        politica_expiracion: PoliticaExpiracionMedia | None = None,
    ) -> None:
        self._media_repo = media_repo
        self._politica = politica_expiracion or PoliticaExpiracionMedia()

    async def __call__(
        self,
        data: RegistrarDescargaMediaIn,
        ahora: datetime,
        media_actual: ArchivoMediaPortafolio | None,
    ) -> RegistrarDescargaMediaOut:
        if media_actual is None:
            raise MediaNoEncontradaError(media_id=data.media_id)

        if media_actual.estado == EstadoMedia.ELIMINADO:
            raise MediaExpiradaError(media_id=data.media_id)

        fecha_eliminacion = self._politica.calcular_fecha_eliminacion(ahora)

        await self._media_repo.registrar_descarga(
            media_id=data.media_id,
            fecha_descarga=ahora,
            fecha_eliminacion_programada=fecha_eliminacion,
        )

        media_list = await self._media_repo.listar_por_actividad(media_actual.actividad_id)
        media_actualizada = next((m for m in media_list if m.id == data.media_id), None)
        if media_actualizada is None:
            raise MediaNoEncontradaError(media_id=data.media_id)

        return RegistrarDescargaMediaOut(media=media_actualizada)

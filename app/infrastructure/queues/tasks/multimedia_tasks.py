# app/infrastructure/tasks/multimedia_tasks.py
from __future__ import annotations

import asyncio
from typing import Optional, cast

# 1. IMPORTAR ASYNCSESSION
from sqlalchemy.ext.asyncio import AsyncSession

# 2. IMPORTAR EL MODELO (Para que el IDE sepa qué atributos tiene 'media')
from app.infrastructure.db.models.portafolio.actividad_media import ActividadMedia

from app.infrastructure.db.session import get_session
from app.infrastructure.db.repositories.portafolio.actividad_media_repo import (
    ActividadMediaRepository,
)
from app.infrastructure.storage.local_fs import LocalFileStorage
from app.infrastructure.storage.watermarker import Watermarker


def procesar_watermark_media(media_id: int) -> None:
    """
    Entry-point síncrono para RQ: delega en una corrutina async.
    """
    asyncio.run(_procesar_watermark_media_async(media_id))


async def _procesar_watermark_media_async(media_id: int) -> None:
    # 3. TIPAR LA SESIÓN (Soluciona el .commit() marcado como Any)
    session: AsyncSession
    async with get_session() as session:
        
        repo = ActividadMediaRepository(session)

        # 4. TIPAR EL RESULTADO (Soluciona el media.ruta_archivo marcado como Any)
        # Al poner ": Optional[ActividadMedia]", conectamos este objeto con la clase importada arriba.
        media: Optional[ActividadMedia] = await repo.obtener_por_id(media_id)

        if media is None:
            return

        # Ahora el IDE sabe que 'media' tiene el atributo 'procesado'
        if getattr(media, "procesado", False):
            return

        storage = LocalFileStorage()
        wm = Watermarker(text="Datilera")

        # El IDE ahora reconoce que ruta_archivo es un str
        ruta_relativa: str = media.url
        archivo_path = storage.get_full_path(ruta_relativa)

        wm.apply_watermark(archivo_path)

        await repo.marcar_como_procesado(media_id)
        
        # El IDE ahora reconoce el método commit
        await session.commit()
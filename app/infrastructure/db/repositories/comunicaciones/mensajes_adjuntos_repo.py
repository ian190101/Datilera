# app/infrastructure/db/repositories/comunicaciones/mensajes_adjuntos_repo.py
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.db.repositories.base import BaseRepository
from app.infrastructure.db.models.comunicaciones import MensajeAdjunto
from typing import List

class MensajesAdjuntosRepository(BaseRepository[MensajeAdjunto]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, MensajeAdjunto)
    async def listar_por_mensaje(self, mensaje_id: int) -> List[MensajeAdjunto]:
        """Listar adjuntos de un mensaje."""
        query = select(MensajeAdjunto).where(
            MensajeAdjunto.mensaje_id == mensaje_id
        ).order_by(MensajeAdjunto.creado_en.asc())
        result = await self.session.execute(query)
        return result.scalars().all()
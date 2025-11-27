from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.repositories.base import BaseRepository
from app.infrastructure.db.models.comunicaciones import MensajeLeido

class MensajesLecturasRepository(BaseRepository[MensajeLeido]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, MensajeLeido)
    
    async def ya_leido(self, mensaje_id: int, usuario_id: int) -> bool:
        """Verificar si un mensaje ya fue leído."""
        query = select(MensajeLeido).where(
            MensajeLeido.mensaje_id == mensaje_id,
            MensajeLeido.usuario_id == usuario_id
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none() is not None

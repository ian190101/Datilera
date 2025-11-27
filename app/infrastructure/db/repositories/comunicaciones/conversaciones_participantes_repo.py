from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.infrastructure.db.repositories.base import BaseRepository
from app.infrastructure.db.models.comunicaciones import ConversacionParticipante

class ConversacionesParticipantesRepository(BaseRepository[ConversacionParticipante]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, ConversacionParticipante)
    
    async def listar_por_conversacion(self, conversacion_id: int) -> List[ConversacionParticipante]:
        """Listar participantes de una conversación."""
        query = select(ConversacionParticipante).where(
            ConversacionParticipante.conversacion_id == conversacion_id
        )
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def es_participante(self, conversacion_id: int, usuario_id: int) -> bool:
        """Verificar si un usuario es participante."""
        query = select(ConversacionParticipante).where(
            ConversacionParticipante.conversacion_id == conversacion_id,
            ConversacionParticipante.usuario_id == usuario_id
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none() is not None
    
    async def remover(self, conversacion_id: int, usuario_id: int) -> bool:
        """Remover un participante."""
        query = delete(ConversacionParticipante).where(
            ConversacionParticipante.conversacion_id == conversacion_id,
            ConversacionParticipante.usuario_id == usuario_id
        )
        result = await self.session.execute(query)
        await self.session.commit()
        return result.rowcount > 0

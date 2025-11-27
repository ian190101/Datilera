from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.infrastructure.db.repositories.base import BaseRepository
from app.infrastructure.db.models.comunicaciones import Conversacion
from app.infrastructure.db.models.comunicaciones import ConversacionParticipante

class ConversacionesRepository(BaseRepository[Conversacion]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Conversacion)
    
    async def listar_por_usuario(
        self, 
        usuario_id: int,
        sede_id: Optional[int] = None,
        cerradas: Optional[bool] = None,
        limite: int = 20,
        offset: int = 0
    ) -> List[Conversacion]:
        """Listar conversaciones donde el usuario es participante."""
        query = select(Conversacion).join(
            ConversacionParticipante,
            ConversacionParticipante.conversacion_id == Conversacion.id
        ).where(ConversacionParticipante.usuario_id == usuario_id)
        
        if sede_id:
            query = query.where(Conversacion.sede_id == sede_id)
        
        if cerradas is not None:
            query = query.where(Conversacion.cerrado == cerradas)
        
        query = query.order_by(Conversacion.ultima_actividad_en.desc()).limit(limite).offset(offset)
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def buscar_por_asunto(self, usuario_id: int, termino: str, limite: int = 20) -> List[Conversacion]:
        """Buscar conversaciones por asunto."""
        query = select(Conversacion).join(
            ConversacionParticipante,
            ConversacionParticipante.conversacion_id == Conversacion.id
        ).where(
            and_(
                ConversacionParticipante.usuario_id == usuario_id,
                Conversacion.asunto.ilike(f"%{termino}%")
            )
        ).order_by(Conversacion.ultima_actividad_en.desc()).limit(limite)
        result = await self.session.execute(query)
        return result.scalars().all()

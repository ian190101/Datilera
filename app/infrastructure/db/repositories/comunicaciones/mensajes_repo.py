from sqlalchemy import select, func, case, and_
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Optional
from sqlalchemy.engine import Row


from app.infrastructure.db.repositories.base import BaseRepository
from app.infrastructure.db.models.comunicaciones.mensajes_lecturas import MensajeLeido
from app.infrastructure.db.models.comunicaciones.mensajes import Mensaje
from app.infrastructure.db.models.comunicaciones.conversaciones_participantes import ConversacionParticipante


class MensajesRepository(BaseRepository[Mensaje]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Mensaje)
    
    async def listar_por_conversacion(
        self, 
        conversacion_id: int,
        limite: int = 50,
        offset: int = 0
    ) -> List[Mensaje]:
        """Listar mensajes de una conversación."""
        query = select(Mensaje).where(
            Mensaje.conversacion_id == conversacion_id
        ).order_by(Mensaje.enviado_en.asc()).limit(limite).offset(offset)
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def contar_no_leidos_conversacion(self, conversacion_id: int, usuario_id: int) -> int:
        """Contar mensajes no leídos en una conversación."""
        query = select(func.count(Mensaje.id)).where(
            and_(
                Mensaje.conversacion_id == conversacion_id,
                Mensaje.remitente_id != usuario_id,
                ~Mensaje.id.in_(
                    select(MensajeLeido.mensaje_id).where(MensajeLeido.usuario_id == usuario_id)
                )
            )
        )
        result = await self.session.execute(query)
        return result.scalar() or 0
    
    async def buscar_por_contenido(self, usuario_id: int, termino: str, limite: int = 20) -> List[Mensaje]:
        """Buscar mensajes por contenido."""
        
        query = select(Mensaje).join(
            ConversacionParticipante,
            ConversacionParticipante.conversacion_id == Mensaje.conversacion_id
        ).where(
            and_(
                ConversacionParticipante.usuario_id == usuario_id,
                Mensaje.contenido.ilike(f"%{termino}%")
            )
        ).order_by(Mensaje.enviado_en.desc()).limit(limite)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def contar_enviados_recibidos(self, usuario_id: int, conversacion_id: Optional[int] = None) -> Dict[str, int]:
        """Contar mensajes enviados vs recibidos."""
        
        
        query = select(
            func.sum(case((Mensaje.remitente_id == usuario_id, 1), else_=0)).label('enviados'),
            func.sum(case((Mensaje.remitente_id != usuario_id, 1), else_=0)).label('recibidos')
        )
        
        if conversacion_id:
            query = query.where(Mensaje.conversacion_id == conversacion_id)
        else:
            
            query = query.join(
                ConversacionParticipante,
                ConversacionParticipante.conversacion_id == Mensaje.conversacion_id
            ).where(ConversacionParticipante.usuario_id == usuario_id)
        
        result = await self.session.execute(query)
        row: Row = result.one()
        # Acceso por índice con cast explícito
        enviados = int(row[0]) if row[0] is not None else 0
        recibidos = int(row[1]) if row[1] is not None else 0
        return {
            'enviados': enviados,
            'recibidos': recibidos
        }

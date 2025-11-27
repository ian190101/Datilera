from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict
from datetime import datetime
from sqlalchemy.engine import Row

from app.infrastructure.db.repositories.base import BaseRepository
from app.infrastructure.db.models.comunicaciones import Notificacion

class NotificacionesRepository(BaseRepository[Notificacion]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Notificacion)
    
    async def listar_por_usuario(
        self, 
        usuario_id: int, 
        tipo: Optional[str] = None,
        leidas: Optional[bool] = None,
        limite: int = 20,
        offset: int = 0
    ) -> List[Notificacion]:
        """Listar notificaciones con filtros."""
        query = select(Notificacion).where(Notificacion.usuario_id == usuario_id)
        
        if tipo:
            query = query.where(Notificacion.tipo == tipo)
        
        if leidas is not None:
            if leidas:
                query = query.where(Notificacion.leido_en.isnot(None))
            else:
                query = query.where(Notificacion.leido_en.is_(None))
        
        query = query.order_by(Notificacion.creado_en.desc()).limit(limite).offset(offset)
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def contar_no_leidas(self, usuario_id: int) -> int:
        """Contar notificaciones no leídas."""
        query = select(func.count(Notificacion.id)).where(
            and_(
                Notificacion.usuario_id == usuario_id,
                Notificacion.leido_en.is_(None)
            )
        )
        result = await self.session.execute(query)
        return result.scalar() or 0
    
    async def marcar_todas_leidas(self, usuario_id: int) -> int:
        """Marcar todas como leídas."""
        from sqlalchemy import update
        query = update(Notificacion).where(
            and_(
                Notificacion.usuario_id == usuario_id,
                Notificacion.leido_en.is_(None)
            )
        ).values(leido_en=datetime.utcnow())
        result = await self.session.execute(query)
        await self.session.commit()
        return result.rowcount
    
    async def obtener_programadas_pendientes(self, hasta: datetime) -> List[Notificacion]:
        """Obtener notificaciones programadas pendientes."""
        query = select(Notificacion).where(
            and_(
                Notificacion.programada_para.isnot(None),
                Notificacion.programada_para <= hasta,
                Notificacion.enviado == False
            )
        ).order_by(Notificacion.programada_para)
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def contar_por_tipo(self, usuario_id: int) -> Dict[str, int]:
        """Contar notificaciones agrupadas por tipo."""
        from sqlalchemy import func
        query = select(
            Notificacion.tipo,
            func.count(Notificacion.id).label('total')
        ).where(
            Notificacion.usuario_id == usuario_id
        ).group_by(Notificacion.tipo)
        result = await self.session.execute(query)
        rows: List[Row] = result.all()  # ← Tipo explícito
        
        # Acceso por índice con tipos explícitos
        return {str(row[0]): int(row[1]) for row in rows}


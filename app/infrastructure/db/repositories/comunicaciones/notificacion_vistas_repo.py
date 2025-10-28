# app/infrastructure/db/repositories/comunicaciones/notificacion_vistas_repo.py
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.db.repositories.base import BaseRepository
from app.infrastructure.db.models.comunicaciones import NotificacionVista

class NotificacionVistasRepository(BaseRepository[NotificacionVista]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, NotificacionVista)

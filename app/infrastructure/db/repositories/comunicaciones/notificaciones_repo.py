# app/infrastructure/db/repositories/comunicaciones/notificaciones_repo.py
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.db.repositories.base import BaseRepository
from app.infrastructure.db.models.comunicaciones import Notificacion

class NotificacionesRepository(BaseRepository[Notificacion]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Notificacion)

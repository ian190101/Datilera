# app/infrastructure/db/repositories/comunicaciones/mensajes_repo.py
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.db.repositories.base import BaseRepository
from app.infrastructure.db.models.comunicaciones import Mensaje

class MensajesRepository(BaseRepository[Mensaje]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Mensaje)

# app/infrastructure/db/repositories/comunicaciones/conversaciones_repo.py
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.db.repositories.base import BaseRepository
from app.infrastructure.db.models.comunicaciones import Conversacion

class ConversacionesRepository(BaseRepository[Conversacion]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Conversacion)

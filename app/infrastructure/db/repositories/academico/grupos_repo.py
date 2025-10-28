# app/infrastructure/db/repositories/academico/grupos_repo.py
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.db.repositories.base import BaseRepository
from app.infrastructure.db.models.academico import Grupo

class GruposRepository(BaseRepository[Grupo]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Grupo)

# app/infrastructure/db/repositories/academico/paralelos_repo.py
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.db.repositories.base import BaseRepository
from app.infrastructure.db.models.academico import Paralelo

class ParalelosRepository(BaseRepository[Paralelo]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Paralelo)

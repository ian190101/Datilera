# app/infrastructure/db/repositories/finanzas/arqueos_repo.py
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.db.repositories.base import BaseRepository
from app.infrastructure.db.models.finanzas import Arqueo

class ArqueosRepository(BaseRepository[Arqueo]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Arqueo)

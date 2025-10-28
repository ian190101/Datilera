# app/infrastructure/db/repositories/finanzas/conciliaciones_repo.py
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.db.repositories.base import BaseRepository
from app.infrastructure.db.models.finanzas import Conciliacion

class ConciliacionesRepository(BaseRepository[Conciliacion]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Conciliacion)

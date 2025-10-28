# app/infrastructure/db/repositories/finanzas/turnos_repo.py
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.db.repositories.base import BaseRepository
from app.infrastructure.db.models.finanzas import Turno

class TurnosRepository(BaseRepository[Turno]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Turno)

# app/infrastructure/db/repositories/academico/horarios_paralelos_repo.py
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.db.repositories.base import BaseRepository
from app.infrastructure.db.models.academico import HorarioParalelo

class HorariosParalelosRepository(BaseRepository[HorarioParalelo]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, HorarioParalelo)

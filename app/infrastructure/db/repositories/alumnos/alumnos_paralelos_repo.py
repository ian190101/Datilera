# app/infrastructure/db/repositories/alumnos/alumnos_paralelos_repo.py
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.db.repositories.base import BaseRepository
from app.infrastructure.db.models.alumnos import AlumnoParalelo

class AlumnosParalelosRepository(BaseRepository[AlumnoParalelo]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, AlumnoParalelo)

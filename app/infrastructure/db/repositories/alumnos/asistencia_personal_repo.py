# app/infrastructure/db/repositories/alumnos/asistencia_personal_repo.py
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.db.repositories.base import BaseRepository
from app.infrastructure.db.models.alumnos import AsistenciaPersonal

class AsistenciaPersonalRepository(BaseRepository[AsistenciaPersonal]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, AsistenciaPersonal)

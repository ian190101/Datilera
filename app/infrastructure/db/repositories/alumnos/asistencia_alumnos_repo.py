# app/infrastructure/db/repositories/alumnos/asistencia_alumnos_repo.py
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.db.repositories.base import BaseRepository
from app.infrastructure.db.models.alumnos import AsistenciaAlumno

class AsistenciaAlumnosRepository(BaseRepository[AsistenciaAlumno]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, AsistenciaAlumno)

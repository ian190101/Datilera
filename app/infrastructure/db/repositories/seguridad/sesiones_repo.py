# app/infrastructure/db/repositories/seguridad/sesiones_repo.py
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.db.repositories.base import BaseRepository
from app.infrastructure.db.models.seguridad import Sesion

class SesionesRepository(BaseRepository[Sesion]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Sesion)

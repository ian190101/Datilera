# app/infrastructure/db/repositories/alumnos/permisos_personal_repo.py
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.db.repositories.base import BaseRepository
from app.infrastructure.db.models.alumnos import PermisoPersonal

class PermisosPersonalRepository(BaseRepository[PermisoPersonal]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, PermisoPersonal)

# app/infrastructure/db/repositories/seguridad/permisos_repo.py
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.db.repositories.base import BaseRepository
from app.infrastructure.db.models.seguridad import Permiso

class PermisosRepository(BaseRepository[Permiso]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Permiso)

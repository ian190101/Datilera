# app/infrastructure/db/repositories/seguridad/roles_repo.py
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.db.repositories.base import BaseRepository
from app.infrastructure.db.models.seguridad import Rol

class RolesRepository(BaseRepository[Rol]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Rol)

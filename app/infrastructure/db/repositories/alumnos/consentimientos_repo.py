# app/infrastructure/db/repositories/alumnos/consentimientos_repo.py
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.db.repositories.base import BaseRepository
from app.infrastructure.db.models.alumnos import Consentimiento

class ConsentimientosRepository(BaseRepository[Consentimiento]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Consentimiento)

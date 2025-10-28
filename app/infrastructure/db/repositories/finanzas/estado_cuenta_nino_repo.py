# app/infrastructure/db/repositories/finanzas/estado_cuenta_nino_repo.py
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.db.repositories.base import BaseRepository
from app.infrastructure.db.models.finanzas import EstadoCuentaNino

class EstadoCuentaNinoRepository(BaseRepository[EstadoCuentaNino]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, EstadoCuentaNino)

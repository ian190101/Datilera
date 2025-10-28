# app/infrastructure/db/repositories/finanzas/libro_caja_repo.py
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.db.repositories.base import BaseRepository
from app.infrastructure.db.models.finanzas import LibroCaja

class LibroCajaRepository(BaseRepository[LibroCaja]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, LibroCaja)

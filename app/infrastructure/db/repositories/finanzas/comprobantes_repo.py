# app/infrastructure/db/repositories/finanzas/comprobantes_repo.py
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.db.repositories.base import BaseRepository
from app.infrastructure.db.models.finanzas import Comprobante

class ComprobantesRepository(BaseRepository[Comprobante]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Comprobante)

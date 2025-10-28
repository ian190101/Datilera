# app/infrastructure/db/repositories/finanzas/categorias_pago_repo.py
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.db.repositories.base import BaseRepository
from app.infrastructure.db.models.finanzas import CategoriaPago

class CategoriasPagoRepository(BaseRepository[CategoriaPago]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, CategoriaPago)

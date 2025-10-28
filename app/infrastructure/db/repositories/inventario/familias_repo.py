# app/infrastructure/db/repositories/inventario/familias_repo.py
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.db.repositories.base import BaseRepository
from app.infrastructure.db.models.inventario import Familia

class FamiliasRepository(BaseRepository[Familia]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Familia)

# app/infrastructure/db/repositories/inventario/stock_sede_repo.py
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.db.repositories.base import BaseRepository
from app.infrastructure.db.models.inventario import StockSede

class StockSedeRepository(BaseRepository[StockSede]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, StockSede)

# app/infrastructure/db/repositories/inventario/stock_sede_repo.py
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.db.repositories.base import BaseRepository
from app.infrastructure.db.models.inventario import StockSede

class StockSedeRepository(BaseRepository[StockSede]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, StockSede)

    async def list_por_sede(self, sede_id: int):
        return await self.list(where=(StockSede.sede_id == sede_id,))

    async def get_por_item_sede(self, item_id: int, sede_id: int):
        return await self.one(where=((StockSede.item_id == item_id), (StockSede.sede_id == sede_id)))
# app/infrastructure/db/repositories/inventario/movimientos_stock_repo.py
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.db.repositories.base import BaseRepository
from app.infrastructure.db.models.inventario import MovimientoStock

class MovimientosStockRepository(BaseRepository[MovimientoStock]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, MovimientoStock)

async def list_por_item(self, item_id: int):
        return await self.list(where=(MovimientoStock.item_id == item_id,))
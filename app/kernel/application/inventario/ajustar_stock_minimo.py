# app/kernel/application/inventario/ajustar_stock_minimo.py
from app.infrastructure.db.repositories.inventario.stock_sede_repo import StockSedeRepository

class AjustarStockMinimo:
    def __init__(self, repo: StockSedeRepository):
        self.repo = repo

    async def execute(self, item_id: int, sede_id: int, minimo: float) -> None:
        await self.repo.upsert_minimo(item_id, sede_id, minimo)

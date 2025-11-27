# app/kernel/application/inventario/get_stock_por_sede.py
from pydantic import BaseModel, ConfigDict
from decimal import Decimal
from typing import List
from app.infrastructure.db.repositories.inventario.stock_sede_repo import StockSedeRepository

class GetStockPorSede:
    def __init__(self, repo: StockSedeRepository):
        self.repo = repo

    async def execute(self, sede_id: int):
        rows = await self.repo.list_por_sede(sede_id)
        return [{"item_id": r.item_id, "cantidad": str(r.cantidad_disponible), "minimo": str(r.stock_minimo)} for r in rows]
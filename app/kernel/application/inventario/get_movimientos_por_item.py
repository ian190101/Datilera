# app/kernel/application/inventario/get_movimientos_por_item.py
from __future__ import annotations
from typing import List
from decimal import Decimal
from datetime import date
from pydantic import BaseModel, ConfigDict

from app.infrastructure.db.repositories.inventario.movimientos_stock_repo import MovimientosStockRepository

class MovimientoDTO(BaseModel):
    id: int
    item_id: int
    sede_id: int
    tipo: str
    cantidad: Decimal
    usuario_id: int
    fecha_movimiento: date
    motivo: str | None = None
    referencia: str | None = None
    model_config = ConfigDict(from_attributes=True)

class GetMovimientosPorItem:
    def __init__(self, repo: MovimientosStockRepository):
        self.repo = repo

    async def execute(self, item_id: int) -> List[MovimientoDTO]:
        rows = await self.repo.list_por_item(item_id)
        # Si necesitas ordenar por fecha desc y tu repo no lo hace, ordénalo aquí
        rows = sorted(rows, key=lambda r: (r.fecha_movimiento, r.id), reverse=True)
        return [
            MovimientoDTO(
                id=r.id, item_id=r.item_id, sede_id=r.sede_id, tipo=getattr(r.tipo, "value", str(r.tipo)),
                cantidad=r.cantidad, usuario_id=r.usuario_id, fecha_movimiento=r.fecha_movimiento,
                motivo=r.motivo, referencia=r.referencia
            )
            for r in rows
        ]

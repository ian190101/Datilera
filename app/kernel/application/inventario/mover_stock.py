# app/kernel/application/inventario/mover_stock.py
from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Optional, Literal

from pydantic import BaseModel, Field, field_validator

from app.infrastructure.db.repositories.inventario.stock_sede_repo import StockSedeRepository
from app.infrastructure.db.repositories.inventario.movimientos_stock_repo import MovimientosStockRepository
from app.infrastructure.db.models.inventario import StockSede as StockSedeModel
from app.infrastructure.db.models.inventario import MovimientoStock as MovimientoModel
from app.infrastructure.db.models.inventario.movimientos_stock import TipoMovimiento as TipoMovModel

class MoverStockRequest(BaseModel):
    item_id: int
    sede_id: int
    tipo: Literal["entrada", "salida", "ajuste", "transferencia"]
    cantidad: Decimal = Field(..., gt=0)
    usuario_id: int
    motivo: Optional[str] = None
    referencia: Optional[str] = None
    fecha_movimiento: date = Field(default_factory=date.today)
    sede_destino_id: Optional[int] = None  # solo transferencia
    ajuste_sentido: Optional[Literal[1, -1]] = None  # solo ajuste (opcional)

    @field_validator("sede_destino_id")
    @classmethod
    def validar_transferencia(cls, v, values):
        if values.get("tipo") == "transferencia" and not v:
            raise ValueError("sede_destino_id es obligatorio para transferencia.")
        return v

class MovimientoResponse(BaseModel):
    id: int
    item_id: int
    sede_id: int
    tipo: str
    cantidad: Decimal
    usuario_id: int
    fecha_movimiento: date

class MoverStock:
    """
    Registra el movimiento y actualiza stock_sede; transferencia = salida origen + entrada destino.
    """
    def __init__(self, stock_repo: StockSedeRepository, mov_repo: MovimientosStockRepository):
        self.stock_repo = stock_repo
        self.mov_repo = mov_repo

    async def _get_or_create_stock(self, item_id: int, sede_id: int) -> StockSedeModel:
        row = await self.stock_repo.one(where=(
            (StockSedeModel.item_id == item_id),
            (StockSedeModel.sede_id == sede_id),
        ))
        if row:
            return row
        return await self.stock_repo.create(StockSedeModel(
            item_id=item_id, sede_id=sede_id, cantidad_disponible=0, stock_minimo=0
        ))

    async def _aplicar_delta(self, st: StockSedeModel, delta: Decimal) -> None:
        nueva = Decimal(st.cantidad_disponible) + Decimal(delta)
        if nueva < 0:
            raise ValueError("Stock insuficiente para la operación.")
        await self.stock_repo.update(st.id, {"cantidad_disponible": nueva})

    async def _registrar_mov(self, req: MoverStockRequest, sede_id: int, tipo: str, cantidad: Decimal) -> MovimientoResponse:
        mov = await self.mov_repo.create(MovimientoModel(
            item_id=req.item_id,
            sede_id=sede_id,
            tipo=TipoMovModel[tipo] if hasattr(TipoMovModel, tipo) else TipoMovModel(tipo),
            cantidad=cantidad,
            usuario_id=req.usuario_id,
            motivo=req.motivo,
            referencia=req.referencia,
            fecha_movimiento=req.fecha_movimiento,
        ))
        return MovimientoResponse(
            id=mov.id, item_id=mov.item_id, sede_id=mov.sede_id, tipo=mov.tipo.value,
            cantidad=mov.cantidad, usuario_id=mov.usuario_id, fecha_movimiento=mov.fecha_movimiento
        )

    async def execute(self, req: MoverStockRequest) -> list[MovimientoResponse]:
        respuestas: list[MovimientoResponse] = []

        if req.tipo == "transferencia":
            st_origen = await self._get_or_create_stock(req.item_id, req.sede_id)
            await self._aplicar_delta(st_origen, Decimal(-req.cantidad))
            respuestas.append(await self._registrar_mov(req, req.sede_id, "salida", req.cantidad))

            st_dest = await self._get_or_create_stock(req.item_id, int(req.sede_destino_id))
            await self._aplicar_delta(st_dest, Decimal(req.cantidad))
            respuestas.append(await self._registrar_mov(req, int(req.sede_destino_id), "entrada", req.cantidad))
            return respuestas

        st = await self._get_or_create_stock(req.item_id, req.sede_id)
        if req.tipo == "entrada":
            await self._aplicar_delta(st, Decimal(req.cantidad))
            respuestas.append(await self._registrar_mov(req, req.sede_id, "entrada", req.cantidad))
        elif req.tipo == "salida":
            await self._aplicar_delta(st, Decimal(-req.cantidad))
            respuestas.append(await self._registrar_mov(req, req.sede_id, "salida", req.cantidad))
        elif req.tipo == "ajuste":
            sentido = Decimal(req.ajuste_sentido or 1)
            await self._aplicar_delta(st, Decimal(req.cantidad) * sentido)
            respuestas.append(await self._registrar_mov(req, req.sede_id, "ajuste", req.cantidad * sentido))
        else:
            raise ValueError("Tipo de movimiento no soportado.")
        return respuestas

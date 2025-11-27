# app/kernel/application/inventario/generar_alertas.py
from __future__ import annotations

from datetime import date, timedelta
from pydantic import BaseModel

from app.infrastructure.db.repositories.inventario.stock_sede_repo import StockSedeRepository
from app.infrastructure.db.repositories.inventario.alertas_stock_repo import AlertasStockRepository
from app.infrastructure.db.repositories.inventario.alertas_vencimiento_repo import AlertasVencimientoRepository

from app.infrastructure.db.models.inventario import StockSede as StockSedeModel
from app.infrastructure.db.models.inventario import AlertaStock as AlertaStockModel
from app.infrastructure.db.models.inventario import AlertaVencimiento as AlertaVencimientoModel

class GenerarAlertasResponse(BaseModel):
    creadas_stock: int = 0
    vencimientos_pendientes: int = 0

class GenerarAlertasStock:
    """
    Genera alertas de stock bajo cuando cantidad_disponible < stock_minimo si no existe una alerta no resuelta.
    """
    def __init__(self, stock_repo: StockSedeRepository, alertas_repo: AlertasStockRepository):
        self.stock_repo = stock_repo
        self.alertas_repo = alertas_repo

    async def execute(self) -> GenerarAlertasResponse:
        response = GenerarAlertasResponse()
        stocks = await self.stock_repo.list()
        for st in stocks:
            if st.cantidad_disponible < st.stock_minimo:
                exists = await self.alertas_repo.one(where=(
                    (AlertaStockModel.item_id == st.item_id),
                    (AlertaStockModel.sede_id == st.sede_id),
                    (AlertaStockModel.resuelta == False),
                ))
                if not exists:
                    mensaje = f"Stock bajo para item {st.item_id} en sede {st.sede_id} (disp={st.cantidad_disponible}, min={st.stock_minimo})"
                    await self.alertas_repo.create(AlertaStockModel(
                        item_id=st.item_id,
                        sede_id=st.sede_id,
                        mensaje=mensaje,
                        resuelta=False,
                    ))
                    response.creadas_stock += 1
        return response

class GenerarAlertasVencimiento:
    """
    Calcula cuántas alertas de vencimiento están por notificarse a 5/3/1 días u hoy (sin enviar).
    """
    def __init__(self, venc_repo: AlertasVencimientoRepository):
        self.venc_repo = venc_repo

    async def execute(self, dias: list[int] | None = None) -> GenerarAlertasResponse:
        dias = dias or [5, 3, 1, 0]
        hoy = date.today()
        total = 0
        for d in dias:
            objetivo = hoy + timedelta(days=d)
            rows = await self.venc_repo.list(where=(
                (AlertaVencimientoModel.fecha_vencimiento == objetivo),
                (AlertaVencimientoModel.notificada == False),
            ))
            total += len(rows or [])
        return GenerarAlertasResponse(vencimientos_pendientes=total)

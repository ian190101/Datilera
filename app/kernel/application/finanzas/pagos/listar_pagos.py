# app/application/use_cases/finanzas/listar_pagos.py
from datetime import date
from typing import Any, Dict, List

from app.kernel.domain.finanzas.ports import IPagoRepository


class ListarPagosUC:
    def __init__(self, pago_repo: IPagoRepository) -> None:
        self._pago_repo = pago_repo

    async def execute(
        self,
        sede_id: int | None = None,
        alumno_id: int | None = None,
        fecha_desde: date | None = None,
        fecha_hasta: date | None = None,
        metodo_pago: str | None = None,
        incluir_anulados: bool = False,
        limit: int = 100,
        offset: int = 0,
    ) -> dict[str, Any]:
        # Solo anotamos tipos de salida para evitar Any
        items: List[Dict[str, Any]] = await self._pago_repo.listar(
            sede_id=sede_id,
            alumno_id=alumno_id,
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta,
            metodo_pago=metodo_pago,
            incluir_anulados=incluir_anulados,
            limit=limit,
            offset=offset,
        )

        total: int = await self._pago_repo.contar(
            sede_id=sede_id,
            alumno_id=alumno_id,
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta,
            metodo_pago=metodo_pago,
            incluir_anulados=incluir_anulados,
        )

        return {
            "items": items,
            "total": total,
            "limit": limit,
            "offset": offset,
        }

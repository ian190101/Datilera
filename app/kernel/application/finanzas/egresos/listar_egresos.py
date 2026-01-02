# app/application/use_cases/finanzas/listar_egresos.py
from datetime import date
from typing import Any, Dict, List

from app.kernel.domain.finanzas.ports import IEgresoRepository


class ListarEgresosUC:
    def __init__(self, egreso_repo: IEgresoRepository) -> None:
        self._egreso_repo = egreso_repo

    async def execute(
        self,
        sede_id: int | None = None,
        categoria_id: int | None = None,
        fecha_desde: date | None = None,
        fecha_hasta: date | None = None,
        incluir_anulados: bool = False,
        limit: int = 100,
        offset: int = 0,
    ) -> dict[str, Any]:
        items: List[Dict[str, Any]] = await self._egreso_repo.listar(
            sede_id=sede_id,
            categoria_id=categoria_id,
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta,
            incluir_anulados=incluir_anulados,
            limit=limit,
            offset=offset,
        )

        total: int = await self._egreso_repo.contar(
            sede_id=sede_id,
            categoria_id=categoria_id,
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta,
            incluir_anulados=incluir_anulados,
        )

        return {
            "items": items,
            "total": total,
            "limit": limit,
            "offset": offset,
        }

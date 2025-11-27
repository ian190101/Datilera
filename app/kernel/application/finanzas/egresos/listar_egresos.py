# app/application/finanzas/egresos/listar_egresos.py
"""
CU: Listar egresos (movimientos de libro tipo=EGRESO) por sede y período, con filtros.
"""
from dataclasses import dataclass
from datetime import date
from typing import List, Optional
from app.kernel.domain.finanzas import LibroCaja, TipoMovimiento
from app.kernel.domain.finanzas.ports import LibroCajaRepositoryPort


@dataclass
class ListarEgresosQuery:
    sede_id: int
    fecha_inicio: date
    fecha_fin: date
    categoria_egreso_id: Optional[int] = None


class ListarEgresosUseCase:
    def __init__(self, libro_repo: LibroCajaRepositoryPort):
        self.libro_repo = libro_repo

    async def execute(self, q: ListarEgresosQuery) -> List[LibroCaja]:
        egresos = await self.libro_repo.listar_por_sede_y_periodo(
            sede_id=q.sede_id, fecha_inicio=q.fecha_inicio, fecha_fin=q.fecha_fin, tipo=TipoMovimiento.EGRESO
        )
        if q.categoria_egreso_id is not None:
            egresos = [m for m in egresos if m.categoria_egreso_id == q.categoria_egreso_id]
        return egresos

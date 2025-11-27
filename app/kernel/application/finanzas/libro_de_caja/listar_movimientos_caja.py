# app/application/finanzas/libro_de_caja/listar_movimientos_caja.py
"""
CU: Listar Movimientos de Libro de Caja
"""
from dataclasses import dataclass
from datetime import date
from typing import List, Optional

from app.kernel.domain.finanzas import LibroCaja, TipoMovimiento
from app.kernel.domain.finanzas.ports import LibroCajaRepositoryPort


@dataclass
class ListarMovimientosCajaQuery:
    """Query para listar movimientos de caja"""
    sede_id: int
    fecha_inicio: date
    fecha_fin: date
    tipo: Optional[TipoMovimiento] = None


class ListarMovimientosCajaUseCase:
    """Caso de uso: Listar movimientos del libro de caja"""

    def __init__(self, libro_repo: LibroCajaRepositoryPort):
        self.libro_repo = libro_repo

    async def execute(self, query: ListarMovimientosCajaQuery) -> List[LibroCaja]:
        """Lista movimientos ordenados por fecha descendente"""
        return await self.libro_repo.listar_por_sede_y_periodo(
            sede_id=query.sede_id,
            fecha_inicio=query.fecha_inicio,
            fecha_fin=query.fecha_fin,
            tipo=query.tipo
        )

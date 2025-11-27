# app/application/finanzas/categoria_egreso/listar_categorias_egreso.py
"""
CU: Listar Categorías de Egreso por Sede
"""
from dataclasses import dataclass
from typing import List

from app.kernel.domain.finanzas import CategoriaEgreso
from app.kernel.domain.finanzas.ports import CategoriaEgresoRepositoryPort


@dataclass
class ListarCategoriasEgresoQuery:
    """Query para listar categorías de egreso"""
    sede_id: int
    solo_activas: bool = True


class ListarCategoriasEgresoUseCase:
    """Caso de uso: Listar categorías de egreso de una sede"""

    def __init__(self, categoria_repo: CategoriaEgresoRepositoryPort):
        self.categoria_repo = categoria_repo

    async def execute(self, query: ListarCategoriasEgresoQuery) -> List[CategoriaEgreso]:
        """Lista categorías de egreso ordenadas alfabéticamente"""
        return await self.categoria_repo.listar_por_sede(
            sede_id=query.sede_id,
            solo_activas=query.solo_activas
        )

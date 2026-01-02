# app/application/finanzas/categoria_pago/listar_categorias_pago.py
"""
CU: Listar Categorías de Pago por Sede
"""
from dataclasses import dataclass
from typing import List

from app.kernel.domain.finanzas import CategoriaPago
from app.kernel.domain.finanzas.ports import ICategoriaPagoRepository


@dataclass
class ListarCategoriasPagoQuery:
    """Query para listar categorías de pago"""
    sede_id: int
    solo_activas: bool = True


class ListarCategoriasPagoUseCase:
    """Caso de uso: Listar categorías de pago de una sede"""

    def __init__(self, categoria_repo: ICategoriaPagoRepository):
        self.categoria_repo = categoria_repo

    async def execute(self, query: ListarCategoriasPagoQuery) -> List[CategoriaPago]:
        """Lista categorías de pago ordenadas alfabéticamente"""
        return await self.categoria_repo.listar_por_sede(
            sede_id=query.sede_id,
            solo_activas=query.solo_activas
        )

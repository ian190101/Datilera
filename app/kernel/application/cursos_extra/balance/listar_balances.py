# app/kernel/application/cursosextra/balance/listar_balances.py

"""
Caso de Uso: Listar Balances
"""
from typing import List

from app.kernel.domain.cursos_extra import (
    BalanceCursoExtra,
    EstadoBalance,
    BalanceCursoExtraRepositoryPort,
)


class ListarBalancesPendientesDTO:
    """DTO de entrada para listar balances pendientes."""
    def __init__(self, curso_id: int):
        self.curso_id = curso_id


class ListarBalances:
    """
    Caso de Uso: Listar balances con diferentes filtros.
    """
    
    def __init__(self, balance_repo: BalanceCursoExtraRepositoryPort):
        self.balance_repo = balance_repo
    
    async def pendientes_por_curso(self, dto: ListarBalancesPendientesDTO) -> List[BalanceCursoExtra]:
        """Lista balances pendientes o parciales de un curso."""
        return await self.balance_repo.listar_pendientes_por_curso(dto.curso_id)

# app/kernel/application/cursosextra/pago/listar_pagos.py

"""
Caso de Uso: Listar Pagos
"""
from typing import List

from app.kernel.domain.cursos_extra import (
    PagoCursoExtra,
    PagoCursoExtraRepositoryPort,
)


class ListarPagosPorBalanceDTO:
    """DTO de entrada para listar pagos por balance."""
    def __init__(self, balance_id: int):
        self.balance_id = balance_id


class ListarPagos:
    """
    Caso de Uso: Listar pagos con diferentes filtros.
    """
    
    def __init__(self, pago_repo: PagoCursoExtraRepositoryPort):
        self.pago_repo = pago_repo
    
    async def por_balance(self, dto: ListarPagosPorBalanceDTO) -> List[PagoCursoExtra]:
        """Lista todos los pagos de un balance."""
        return await self.pago_repo.listar_por_balance(dto.balance_id)

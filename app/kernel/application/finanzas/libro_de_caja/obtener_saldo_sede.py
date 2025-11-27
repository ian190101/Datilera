# app/application/finanzas/libro_de_caja/obtener_saldo_sede.py
"""
CU: Obtener saldo actual de caja por sede
"""
from dataclasses import dataclass
from decimal import Decimal
from app.kernel.domain.finanzas.ports import LibroCajaRepositoryPort


@dataclass
class ObtenerSaldoSedeQuery:
    sede_id: int


class ObtenerSaldoSedeUseCase:
    def __init__(self, libro_repo: LibroCajaRepositoryPort):
        self.libro_repo = libro_repo

    async def execute(self, query: ObtenerSaldoSedeQuery) -> Decimal:
        return await self.libro_repo.obtener_saldo_actual(query.sede_id)  # contrato de puerto [attached_file:30]

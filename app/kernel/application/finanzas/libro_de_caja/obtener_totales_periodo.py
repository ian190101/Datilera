# app/application/finanzas/libro_de_caja/obtener_totales_periodo.py
"""
CU: Obtener totales de ingresos, egresos y saldo final del período
"""
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Tuple
from app.kernel.domain.finanzas.ports import LibroCajaRepositoryPort

@dataclass
class ObtenerTotalesPeriodoQuery:
    sede_id: int
    fecha_inicio: date
    fecha_fin: date

class ObtenerTotalesPeriodoUseCase:
    def __init__(self, libro_repo: LibroCajaRepositoryPort):
        self.libro_repo = libro_repo

    async def execute(self, query: ObtenerTotalesPeriodoQuery) -> Tuple[Decimal, Decimal, Decimal]:
        return await self.libro_repo.calcular_totales_periodo(query.sede_id, query.fecha_inicio, query.fecha_fin)  # soporte para reportes/export [attached_file:30]

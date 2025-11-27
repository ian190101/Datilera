# app/application/finanzas/arqueo/recalcular_arqueo.py
"""
CU: Recalcular Arqueo del período
HU: Si aparecen movimientos rezagados, recalcular totales del arqueo.
"""
from dataclasses import dataclass
from app.kernel.domain.finanzas import ArqueoCaja
from app.kernel.domain.finanzas.ports import ArqueoRepositoryPort, LibroCajaRepositoryPort
from app.kernel.domain.finanzas.errors import ArqueoNoEncontrado


@dataclass
class RecalcularArqueoCommand:
    arqueo_id: int


class RecalcularArqueoUseCase:
    def __init__(self, arqueo_repo: ArqueoRepositoryPort, libro_repo: LibroCajaRepositoryPort):
        self.arqueo_repo = arqueo_repo
        self.libro_repo = libro_repo

    async def execute(self, cmd: RecalcularArqueoCommand) -> ArqueoCaja:
        arqueo = await self.arqueo_repo.obtener_por_id(cmd.arqueo_id)
        if not arqueo:
            raise ArqueoNoEncontrado(cmd.arqueo_id)  # validar existencia [attached_file:33]

        total_ing, total_egr, _ = await self.libro_repo.calcular_totales_periodo(
            arqueo.sede_id, arqueo.periodo_inicio, arqueo.periodo_fin
        )
        arqueo.total_ingresos = total_ing
        arqueo.total_egresos = total_egr
        arqueo.recalculado_en = None  # será seteado en repo a now()
        return await self.arqueo_repo.actualizar(arqueo)  # guarda recálculo [attached_file:33]

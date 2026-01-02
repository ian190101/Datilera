# app/application/finanzas/arqueo/generar_arqueo_mensual.py
"""
CU: Generar Arqueo Mensual por sede
HU: Consolidar ingresos/egresos del período y guardar el arqueo.
"""
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from calendar import monthrange

from app.kernel.domain.finanzas import ArqueoCaja  # entidad de arqueo
from app.kernel.domain.finanzas.ports import IArqueoRepository, ILibroCajaRepository
from app.kernel.domain.finanzas.errors import ArqueoError, ArqueoFechaInvalidaError


@dataclass
class GenerarArqueoMensualCommand:
    sede_id: int
    anio: int
    mes: int
    observaciones: str | None = None


class GenerarArqueoMensualUseCase:
    def __init__(self, arqueo_repo: IArqueoRepository, libro_repo: ILibroCajaRepository):
        self.arqueo_repo = arqueo_repo
        self.libro_repo = libro_repo

    async def execute(self, cmd: GenerarArqueoMensualCommand) -> ArqueoCaja:
        if not (1 <= cmd.mes <= 12 and cmd.anio >= 2000):
            raise ArqueoFechaInvalidaError("Período inválido")  # valida período [attached_file:33]
        fin_mes = monthrange(cmd.anio, cmd.mes)[1]
        inicio = date(cmd.anio, cmd.mes, 1)
        fin = date(cmd.anio, cmd.mes, fin_mes)

        existe = await self.arqueo_repo.existe_para_periodo(cmd.sede_id, inicio, fin)
        if existe:
            raise ArqueoError(cmd.sede_id, f"{cmd.anio}-{cmd.mes:02d}")  # no duplicar arqueo [attached_file:33]

        total_ing, total_egr, saldo_final = await self.libro_repo.calcular_totales_periodo(cmd.sede_id, inicio, fin)
        arqueo = ArqueoCaja(
            id=0,
            sede_id=cmd.sede_id,
            periodo_inicio=inicio,
            periodo_fin=fin,
            total_ingresos=Decimal(total_ing),
            total_egresos=Decimal(total_egr),
            observaciones=cmd.observaciones,
        )
        return await self.arqueo_repo.crear(arqueo)  # persistir arqueo [attached_file:33]

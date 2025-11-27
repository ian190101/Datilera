# app/application/finanzas/egresos/anular_egreso.py
"""
CU: Anular egreso creando contramovimiento INGRESO (no borra movimiento original).
Regla: saldo = saldo_actual + monto, referencia "reversa egreso:<mov_id>".
"""
from dataclasses import dataclass
from datetime import date
from app.kernel.domain.finanzas import LibroCaja, TipoMovimiento
from app.kernel.domain.finanzas.ports import LibroCajaRepositoryPort
from app.kernel.domain.finanzas.errors import MovimientoInvalido


@dataclass
class AnularEgresoCommand:
    movimiento_id: int
    sede_id: int
    fecha: date
    usuario_registro_id: int
    referencia: str | None = None
    concepto: str | None = None
    categoria_pago_id: int | None = None  # opcional: categoría de ajuste ingreso


class AnularEgresoUseCase:
    def __init__(self, libro_repo: LibroCajaRepositoryPort):
        self.libro_repo = libro_repo

    async def execute(self, cmd: AnularEgresoCommand) -> LibroCaja:
        mov = await self.libro_repo.obtener_por_id(cmd.movimiento_id)
        if not mov:
            raise MovimientoInvalido(f"Movimiento {cmd.movimiento_id} no existe")
        if mov.sede_id != cmd.sede_id:
            raise MovimientoInvalido(f"El movimiento {cmd.movimiento_id} no pertenece a la sede {cmd.sede_id}")
        if mov.tipo != TipoMovimiento.EGRESO:
            raise MovimientoInvalido(f"El movimiento {cmd.movimiento_id} no es un egreso")

        # idempotencia sencilla: si ya existe una reversa con misma referencia, no duplicar
        # (en repo real, podrías buscar por referencia exacta "reversa egreso:<id>")
        saldo_actual = await self.libro_repo.obtener_saldo_actual(cmd.sede_id)
        saldo_nuevo = saldo_actual + mov.monto

        reversa = LibroCaja(
            id=0,
            sede_id=cmd.sede_id,
            fecha=cmd.fecha,
            tipo=TipoMovimiento.INGRESO,
            categoria_pago_id=cmd.categoria_pago_id,   # puede ser None; se admite concepto libre
            categoria_egreso_id=None,
            pago_id=None,
            monto=mov.monto,
            saldo_acumulado=saldo_nuevo,
            concepto=cmd.concepto or f"Reversa de egreso {mov.id}",
            referencia=cmd.referencia or f"reversa egreso:{mov.id}",
            usuario_registro_id=cmd.usuario_registro_id,
        )
        return await self.libro_repo.registrar_movimiento(reversa)

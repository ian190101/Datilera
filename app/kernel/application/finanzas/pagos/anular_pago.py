# app/application/finanzas/pagos/anular_pago.py
"""
CU: Anular pago creando contramovimiento EGRESO en libro de caja (no borra el pago).
Regla: saldo = saldo_actual - monto, referencia "reversa pago:<id>", mantiene pago_id enlazado.
"""
from dataclasses import dataclass
from datetime import date
from app.kernel.domain.finanzas import LibroCaja, TipoMovimiento
from app.kernel.domain.finanzas.ports import PagoRepositoryPort, LibroCajaRepositoryPort
from app.kernel.domain.finanzas.errors import PagoNoEncontrado, MovimientoInvalido


@dataclass
class AnularPagoCommand:
    pago_id: int
    sede_id: int
    fecha: date
    usuario_registro_id: int
    referencia: str | None = None
    concepto: str | None = None
    categoria_egreso_id: int | None = None  # opcional: categoría de ajuste


class AnularPagoUseCase:
    def __init__(self, pago_repo: PagoRepositoryPort, libro_repo: LibroCajaRepositoryPort):
        self.pago_repo = pago_repo
        self.libro_repo = libro_repo

    async def execute(self, cmd: AnularPagoCommand) -> LibroCaja:
        pago = await self.pago_repo.obtener_por_id(cmd.pago_id)
        if not pago:
            raise PagoNoEncontrado(cmd.pago_id)
        if pago.sede_id != cmd.sede_id:
            raise MovimientoInvalido(f"El pago {cmd.pago_id} no pertenece a la sede {cmd.sede_id}")

        # idempotencia: si ya existe egreso de reversa para este pago, no crear otro
        if await self.libro_repo.existe_egreso_por_pago(pago.id):
            raise MovimientoInvalido(f"El pago {cmd.pago_id} ya fue anulado previamente")

        saldo_actual = await self.libro_repo.obtener_saldo_actual(cmd.sede_id)
        saldo_nuevo = saldo_actual - pago.monto

        movimiento = LibroCaja(
            id=0,
            sede_id=cmd.sede_id,
            fecha=cmd.fecha,
            tipo=TipoMovimiento.EGRESO,
            categoria_pago_id=None,
            categoria_egreso_id=cmd.categoria_egreso_id,  # puede ser None; se admite concepto libre
            pago_id=pago.id,
            monto=pago.monto,
            saldo_acumulado=saldo_nuevo,
            concepto=cmd.concepto or f"Reversa de pago {pago.id}",
            referencia=cmd.referencia or f"reversa pago:{pago.id}",
            usuario_registro_id=cmd.usuario_registro_id,
        )
        return await self.libro_repo.registrar_movimiento(movimiento)

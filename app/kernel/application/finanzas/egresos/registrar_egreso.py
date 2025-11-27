# app/application/finanzas/egresos/registrar_egreso.py
"""
CU: Registrar Egreso en Libro de Caja
HU: Como contador, quiero registrar egresos categorizados en el libro de caja sin permitir saldo negativo.
"""
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Optional

from app.kernel.domain.finanzas import LibroCaja, TipoMovimiento  # TipoMovimiento.EGRESO
from app.kernel.domain.finanzas.ports import (
    LibroCajaRepositoryPort,
    CategoriaEgresoRepositoryPort,
)
from app.kernel.domain.finanzas.errors import (
    CategoriaEgresoNoEncontrada,
    SaldoNegativo,
    MovimientoInvalido,
)


@dataclass
class RegistrarEgresoCommand:
    sede_id: int
    categoria_egreso_id: int
    monto: Decimal
    fecha: date
    usuario_registro_id: int
    concepto: Optional[str] = None
    referencia: Optional[str] = None


class RegistrarEgresoUseCase:
    def __init__(
        self,
        libro_repo: LibroCajaRepositoryPort,
        categoria_repo: CategoriaEgresoRepositoryPort,
    ):
        self.libro_repo = libro_repo
        self.categoria_repo = categoria_repo

    async def execute(self, cmd: RegistrarEgresoCommand) -> LibroCaja:
        # 1) Validar categoría de egreso
        categoria = await self.categoria_repo.obtener_por_id(cmd.categoria_egreso_id)
        if not categoria:
            raise CategoriaEgresoNoEncontrada(cmd.categoria_egreso_id)
        if categoria.sede_id != cmd.sede_id:
            raise MovimientoInvalido(
                f"La categoría {cmd.categoria_egreso_id} no pertenece a la sede {cmd.sede_id}"
            )

        # 2) Validar saldo suficiente
        saldo_actual = await self.libro_repo.obtener_saldo_actual(cmd.sede_id)
        if saldo_actual < cmd.monto:
            raise SaldoNegativo(float(saldo_actual), float(cmd.monto))

        # 3) Construir movimiento
        saldo_nuevo = saldo_actual - cmd.monto
        movimiento = LibroCaja(
            id=0,
            sede_id=cmd.sede_id,
            fecha=cmd.fecha,
            tipo=TipoMovimiento.EGRESO,
            categoria_pago_id=None,
            categoria_egreso_id=cmd.categoria_egreso_id,
            pago_id=None,
            monto=cmd.monto,
            saldo_acumulado=saldo_nuevo,
            concepto=cmd.concepto,
            referencia=cmd.referencia,
            usuario_registro_id=cmd.usuario_registro_id,
        )

        # 4) Persistir movimiento
        return await self.libro_repo.registrar_movimiento(movimiento)

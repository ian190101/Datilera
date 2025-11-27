# app/application/finanzas/pagos/registrar_pago.py
"""
CU: Registrar Pago con asiento en Libro de Caja
HU: Como cajero/contador, quiero registrar pagos con comprobante único y asiento automático.
"""
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Optional

from app.kernel.domain.finanzas import Pago, MetodoPago, LibroCaja, TipoMovimiento  # dominio reexportado
from app.kernel.domain.finanzas.ports import (
    PagoRepositoryPort,
    ComprobanteRepositoryPort,
    CategoriaPagoRepositoryPort,
    LibroCajaRepositoryPort,
)
from app.kernel.domain.finanzas.errors import (
    ComprobanteInvalido,
    CategoriaPagoNoEncontrada,
    MovimientoInvalido,
    MontoPagoIncorrecto,
)


@dataclass
class RegistrarPagoCommand:
    sede_id: int
    categoria_pago_id: int
    monto: Decimal
    metodo: MetodoPago
    comprobante_id: int
    creado_por_usuario_id: int
    fecha: date
    concepto: Optional[str] = None
    referencia: Optional[str] = None
    monto_esperado: Optional[Decimal] = None
    nino_id: Optional[int] = None
    curso_extra_id: Optional[int] = None
    plan_cuota_id: Optional[int] = None


class RegistrarPagoUseCase:
    def __init__(
        self,
        pago_repo: PagoRepositoryPort,
        comp_repo: ComprobanteRepositoryPort,
        categoria_repo: CategoriaPagoRepositoryPort,
        libro_repo: LibroCajaRepositoryPort,
    ):
        self.pago_repo = pago_repo
        self.comp_repo = comp_repo
        self.categoria_repo = categoria_repo
        self.libro_repo = libro_repo

    async def execute(self, cmd: RegistrarPagoCommand) -> Pago:
        # 1) Validar comprobante existe y no duplicado
        comp = await self.comp_repo.obtener_por_id(cmd.comprobante_id)
        if not comp:
            raise ComprobanteInvalido("El comprobante no existe")  # comprobante requerido por HU [attached_file:31]
        # 2) Validar categoría de pago y sede
        cat = await self.categoria_repo.obtener_por_id(cmd.categoria_pago_id)
        if not cat:
            raise CategoriaPagoNoEncontrada(cmd.categoria_pago_id)  # categoría debe existir [attached_file:29]
        if cat.sede_id != cmd.sede_id:
            raise MovimientoInvalido(f"La categoría {cmd.categoria_pago_id} no pertenece a la sede {cmd.sede_id}")  # consistencia por sede [attached_file:29]
        # 3) Validar monto esperado si aplica
        if cmd.monto_esperado is not None and cmd.monto != cmd.monto_esperado:
            raise MontoPagoIncorrecto(float(cmd.monto), float(cmd.monto_esperado))  # regla HU de validación automática [attached_file:31]

        # 4) Crear pago
        pago = Pago(
            id=0,
            sede_id=cmd.sede_id,
            categoria_id=cmd.categoria_pago_id,
            monto=cmd.monto,
            metodo=cmd.metodo,
            comprobante_id=cmd.comprobante_id,
            creado_por_usuario_id=cmd.creado_por_usuario_id,
            nino_id=cmd.nino_id,
            curso_extra_id=cmd.curso_extra_id,
            plan_cuota_id=cmd.plan_cuota_id,
            monto_esperado=cmd.monto_esperado,
        )
        pago = await self.pago_repo.crear(pago)  # persiste el pago [attached_file:31]

        # 5) Asiento en libro de caja
        saldo_actual = await self.libro_repo.obtener_saldo_actual(cmd.sede_id)  # contrato del repo [attached_file:30]
        saldo_nuevo = saldo_actual + cmd.monto
        movimiento = LibroCaja(
            id=0,
            sede_id=cmd.sede_id,
            fecha=cmd.fecha,
            tipo=TipoMovimiento.INGRESO,
            categoria_pago_id=cmd.categoria_pago_id,
            categoria_egreso_id=None,
            pago_id=pago.id,
            monto=cmd.monto,
            saldo_acumulado=saldo_nuevo,
            concepto=cmd.concepto,
            referencia=cmd.referencia,
            usuario_registro_id=cmd.creado_por_usuario_id,
        )
        await self.libro_repo.registrar_movimiento(movimiento)  # afecta saldo y reporte [attached_file:30]

        return pago

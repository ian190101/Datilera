# app/application/finanzas/libro_de_caja/registrar_ingreso_caja.py
"""
CU: Registrar Ingreso en Libro de Caja
HU: Como contador, quiero registrar ingresos categorizados en el libro de caja
"""
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Optional

from app.kernel.domain.finanzas import LibroCaja, TipoMovimiento
from app.kernel.domain.finanzas.ports import (
    ILibroCajaRepository,
    ICategoriaPagoRepository,
    IPagoRepository
)
from app.kernel.domain.finanzas.errors import (
    CategoriaPagoNoEncontradaError,
    PagoNoEncontradoError,
    MovimientoNoEncontradoError,
)


@dataclass
class RegistrarIngresoCommand:
    """Comando para registrar ingreso"""
    sede_id: int
    categoria_pago_id: int
    monto: Decimal
    fecha: date
    concepto: Optional[str] = None
    referencia: Optional[str] = None
    pago_id: Optional[int] = None  # Si viene de tabla pagos
    usuario_registro_id: int = None


class RegistrarIngresoCajaUseCase:
    """Caso de uso: Registrar ingreso en libro de caja"""

    def __init__(
        self,
        libro_repo: ILibroCajaRepository,
        categoria_repo: ICategoriaPagoRepository,
        pago_repo: Optional[ILibroCajaRepository] = None
    ):
        self.libro_repo = libro_repo
        self.categoria_repo = categoria_repo
        self.pago_repo = pago_repo

    async def execute(self, command: RegistrarIngresoCommand) -> LibroCaja:
        """
        Registra un ingreso en el libro de caja
        
        Raises:
            CategoriaPagoNoEncontrada: Si la categoría no existe
            PagoNoEncontrado: Si se especifica pago_id que no existe
            MovimientoInvalido: Si los datos son inconsistentes
        """
        # Validar categoría existe y es de la sede
        categoria = await self.categoria_repo.obtener_por_id(command.categoria_pago_id)
        if not categoria:
            raise CategoriaPagoNoEncontradaError(command.categoria_pago_id)
        if categoria.sede_id != command.sede_id:
            raise MovimientoNoEncontradoError(
                f"Categoría {command.categoria_pago_id} no pertenece a sede {command.sede_id}"
            )

        # Validar pago si se especifica
        if command.pago_id and self.pago_repo:
            pago = await self.pago_repo.obtener_por_id(command.pago_id)
            if not pago:
                raise PagoNoEncontradoError(command.pago_id)

        # Obtener saldo actual para calcular nuevo saldo
        saldo_actual = await self.libro_repo.obtener_saldo_actual(command.sede_id)
        nuevo_saldo = saldo_actual + command.monto

        # Crear movimiento
        movimiento = LibroCaja(
            id=0,
            sede_id=command.sede_id,
            fecha=command.fecha,
            tipo=TipoMovimiento.INGRESO,
            categoria_pago_id=command.categoria_pago_id,
            categoria_egreso_id=None,
            pago_id=command.pago_id,
            monto=command.monto,
            saldo_acumulado=nuevo_saldo,
            concepto=command.concepto,
            referencia=command.referencia,
            usuario_registro_id=command.usuario_registro_id
        )

        # Persistir
        return await self.libro_repo.registrar_movimiento(movimiento)

# app/application/finanzas/libro_de_caja/registrar_egreso_caja.py
"""
CU: Registrar Egreso en Libro de Caja
HU: Como contador, quiero registrar egresos categorizados en el libro de caja
"""
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Optional

from app.kernel.domain.finanzas import LibroCaja, TipoMovimiento
from app.kernel.domain.finanzas.ports import (
    LibroCajaRepositoryPort,
    CategoriaEgresoRepositoryPort
)
from app.kernel.domain.finanzas.errors import (
    CategoriaEgresoNoEncontrada,
    SaldoNegativo,
    MovimientoInvalido
)


@dataclass
class RegistrarEgresoCommand:
    """Comando para registrar egreso"""
    sede_id: int
    categoria_egreso_id: int
    monto: Decimal
    fecha: date
    concepto: Optional[str] = None
    referencia: Optional[str] = None
    usuario_registro_id: int = None


class RegistrarEgresoCajaUseCase:
    """Caso de uso: Registrar egreso en libro de caja"""

    def __init__(
        self,
        libro_repo: LibroCajaRepositoryPort,
        categoria_repo: CategoriaEgresoRepositoryPort
    ):
        self.libro_repo = libro_repo
        self.categoria_repo = categoria_repo

    async def execute(self, command: RegistrarEgresoCommand) -> LibroCaja:
        """
        Registra un egreso en el libro de caja
        
        Raises:
            CategoriaEgresoNoEncontrada: Si la categoría no existe
            SaldoNegativo: Si el egreso excede el saldo disponible
            MovimientoInvalido: Si los datos son inconsistentes
        """
        # Validar categoría existe y es de la sede
        categoria = await self.categoria_repo.obtener_por_id(command.categoria_egreso_id)
        if not categoria:
            raise CategoriaEgresoNoEncontrada(command.categoria_egreso_id)
        if categoria.sede_id != command.sede_id:
            raise MovimientoInvalido(
                f"Categoría {command.categoria_egreso_id} no pertenece a sede {command.sede_id}"
            )

        # Obtener saldo actual y validar que no quede negativo
        saldo_actual = await self.libro_repo.obtener_saldo_actual(command.sede_id)
        if saldo_actual < command.monto:
            raise SaldoNegativo(float(saldo_actual), float(command.monto))

        nuevo_saldo = saldo_actual - command.monto

        # Crear movimiento
        movimiento = LibroCaja(
            id=0,
            sede_id=command.sede_id,
            fecha=command.fecha,
            tipo=TipoMovimiento.EGRESO,
            categoria_pago_id=None,
            categoria_egreso_id=command.categoria_egreso_id,
            pago_id=None,
            monto=command.monto,
            saldo_acumulado=nuevo_saldo,
            concepto=command.concepto,
            referencia=command.referencia,
            usuario_registro_id=command.usuario_registro_id
        )

        # Persistir
        return await self.libro_repo.registrar_movimiento(movimiento)

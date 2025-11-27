# app/kernel/application/cursosextra/pago/registrar_pago.py

"""
Caso de Uso: Registrar Pago
"""
from datetime import date
from decimal import Decimal
from typing import Optional

from app.kernel.domain.cursos_extra import (
    PagoCursoExtra,
    MetodoPagoCursoExtra,
    BalanceCursoExtra,
    EstadoBalance,
    PagoCursoExtraRepositoryPort,
    BalanceCursoExtraRepositoryPort,
    IngresoCursoExtraRepositoryPort,
    InscripcionCursoExtraRepositoryPort,
    BalanceNoEncontrado,
    BalanceYaPagado,
    MontoInvalido,
    PagoExcedeSaldo,
)


class RegistrarPagoDTO:
    """DTO de entrada para registrar pago."""
    def __init__(
        self,
        balance_curso_extra_id: int,
        monto: Decimal,
        metodo_pago: MetodoPagoCursoExtra = MetodoPagoCursoExtra.EFECTIVO,
        fecha_pago: date = None,
        comprobante_url: Optional[str] = None,
        numero_transaccion: Optional[str] = None,
        observaciones: Optional[str] = None,
        registrado_por_id: Optional[int] = None,
    ):
        self.balance_curso_extra_id = balance_curso_extra_id
        self.monto = monto
        self.metodo_pago = metodo_pago
        self.fecha_pago = fecha_pago or date.today()
        self.comprobante_url = comprobante_url
        self.numero_transaccion = numero_transaccion
        self.observaciones = observaciones
        self.registrado_por_id = registrado_por_id


class RegistrarPago:
    """
    Caso de Uso: Registrar un pago para una inscripción.
    
    Validaciones:
    - El balance debe existir y no estar completamente pagado
    - El monto debe ser positivo
    - El monto no debe exceder el saldo pendiente
    - Actualiza automáticamente el balance
    - Actualiza el registro de ingresos consolidados del curso
    """
    
    def __init__(
        self,
        pago_repo: PagoCursoExtraRepositoryPort,
        balance_repo: BalanceCursoExtraRepositoryPort,
        ingreso_repo: IngresoCursoExtraRepositoryPort,
        inscripcion_repo: InscripcionCursoExtraRepositoryPort,
    ):
        self.pago_repo = pago_repo
        self.balance_repo = balance_repo
        self.ingreso_repo = ingreso_repo
        self.inscripcion_repo = inscripcion_repo
    
    async def execute(self, dto: RegistrarPagoDTO) -> PagoCursoExtra:
        """Ejecuta el caso de uso."""
        
        # 1. Validar que el balance existe
        balance = await self.balance_repo.obtener_por_id(dto.balance_curso_extra_id)
        if not balance:
            raise BalanceNoEncontrado(dto.balance_curso_extra_id)
        
        # 2. Validar que el balance no está completamente pagado
        if balance.esta_pagado():
            raise BalanceYaPagado(dto.balance_curso_extra_id)
        
        # 3. Validar monto
        if dto.monto <= Decimal("0"):
            raise MontoInvalido("El monto del pago debe ser mayor a 0.")
        
        # 4. Validar que el monto no excede el saldo
        if dto.monto > balance.saldo:
            raise PagoExcedeSaldo(float(dto.monto), float(balance.saldo))
        
        # 5. Crear el pago (inmutable)
        pago = PagoCursoExtra(
            id=0,
            balance_curso_extra_id=dto.balance_curso_extra_id,
            monto=dto.monto,
            fecha_pago=dto.fecha_pago,
            metodo_pago=dto.metodo_pago,
            comprobante_url=dto.comprobante_url,
            numero_transaccion=dto.numero_transaccion,
            observaciones=dto.observaciones,
        )
        
        pago_creado = await self.pago_repo.crear(pago)
        
        # 6. Actualizar el balance
        balance.registrar_pago(dto.monto)
        await self.balance_repo.actualizar_montos(
            balance_id=balance.id,
            monto_pagado=balance.monto_pagado,
            saldo=balance.saldo,
            estado=balance.estado,
        )
        
        # 7. Actualizar ingresos consolidados del curso
        inscripcion = await self.inscripcion_repo.obtener_por_id(
            balance.inscripcion_curso_extra_id
        )
        if inscripcion:
            # Calcular total de ingresos del curso
            total_ingresos = await self.pago_repo.calcular_total_por_curso(
                inscripcion.curso_extra_id
            )
            
            # Obtener o crear registro de ingresos
            ingreso = await self.ingreso_repo.obtener_por_curso(inscripcion.curso_extra_id)
            if ingreso:
                await self.ingreso_repo.actualizar_ingresos(
                    inscripcion.curso_extra_id,
                    total_ingresos
                )
                # Recalcular ganancias
                await self.ingreso_repo.recalcular_ganancias(inscripcion.curso_extra_id)
        
        return pago_creado

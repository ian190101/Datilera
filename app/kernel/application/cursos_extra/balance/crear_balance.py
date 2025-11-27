# app/kernel/application/cursosextra/balance/crear_balance.py

"""
Caso de Uso: Crear Balance
NOTA: Normalmente el balance se crea automáticamente al inscribir un alumno.
Este caso de uso es para casos especiales o correcciones.
"""
from datetime import date
from decimal import Decimal
from typing import Optional

from app.kernel.domain.cursos_extra import (
    BalanceCursoExtra,
    EstadoBalance,
    BalanceCursoExtraRepositoryPort,
    InscripcionCursoExtraRepositoryPort,
    InscripcionNoEncontrada,
    MontoInvalido,
)


class CrearBalanceDTO:
    """DTO de entrada para crear balance."""
    def __init__(
        self,
        inscripcion_curso_extra_id: int,
        monto_total: Decimal,
        fecha_vencimiento: Optional[date] = None,
    ):
        self.inscripcion_curso_extra_id = inscripcion_curso_extra_id
        self.monto_total = monto_total
        self.fecha_vencimiento = fecha_vencimiento


class CrearBalance:
    """
    Caso de Uso: Crear un balance para una inscripción.
    
    Validaciones:
    - La inscripción debe existir
    - El monto total debe ser positivo
    - No debe existir un balance previo para esa inscripción
    """
    
    def __init__(
        self,
        balance_repo: BalanceCursoExtraRepositoryPort,
        inscripcion_repo: InscripcionCursoExtraRepositoryPort,
    ):
        self.balance_repo = balance_repo
        self.inscripcion_repo = inscripcion_repo
    
    async def execute(self, dto: CrearBalanceDTO) -> BalanceCursoExtra:
        """Ejecuta el caso de uso."""
        
        # Validar que la inscripción existe
        inscripcion = await self.inscripcion_repo.obtener_por_id(dto.inscripcion_curso_extra_id)
        if not inscripcion:
            raise InscripcionNoEncontrada(dto.inscripcion_curso_extra_id)
        
        # Validar monto
        if dto.monto_total <= Decimal("0"):
            raise MontoInvalido("El monto total debe ser mayor a 0.")
        
        # Validar que no existe balance previo
        balance_existente = await self.balance_repo.obtener_por_inscripcion(
            dto.inscripcion_curso_extra_id
        )
        if balance_existente:
            raise ValueError(f"Ya existe un balance para la inscripción {dto.inscripcion_curso_extra_id}")
        
        # Crear balance
        balance = BalanceCursoExtra(
            id=0,
            inscripcion_curso_extra_id=dto.inscripcion_curso_extra_id,
            monto_total=dto.monto_total,
            monto_pagado=Decimal("0.00"),
            saldo=dto.monto_total,
            fecha_vencimiento=dto.fecha_vencimiento,
            estado=EstadoBalance.PENDIENTE,
        )
        
        return await self.balance_repo.crear(balance)

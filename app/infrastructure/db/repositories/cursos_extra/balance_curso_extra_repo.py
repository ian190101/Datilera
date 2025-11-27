"""
Repositorio para operaciones de Balance de Cursos Extra.
"""
from sqlalchemy import select, and_, func, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from typing import List, Optional
from decimal import Decimal

from app.infrastructure.db.repositories.base import BaseRepository
from app.infrastructure.db.models.cursos_extra import (
    BalanceCursoExtra,
    EstadoBalance,
    InscripcionCursoExtra
)


class BalanceCursoExtraRepository(BaseRepository[BalanceCursoExtra]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, BalanceCursoExtra)

    async def obtener_por_inscripcion(
        self,
        inscripcion_id: int
    ) -> Optional[BalanceCursoExtra]:
        """Obtiene el balance de una inscripción."""
        query = select(BalanceCursoExtra).where(
            BalanceCursoExtra.inscripcion_curso_extra_id == inscripcion_id
        )

        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def actualizar_montos(
        self,
        balance_id: int,
        monto_pagado: Decimal,
        saldo: Decimal,
        estado: EstadoBalance
    ) -> Optional[BalanceCursoExtra]:
        """Actualiza los montos del balance tras un pago."""
        query = update(BalanceCursoExtra).where(
            BalanceCursoExtra.id == balance_id
        ).values(
            monto_pagado=monto_pagado,
            saldo=saldo,
            estado=estado
        ).returning(BalanceCursoExtra)

        result = await self.session.execute(query)
        await self.session.commit()
        return result.scalar_one_or_none()

    async def listar_pendientes_por_curso(
        self,
        curso_id: int
    ) -> List[BalanceCursoExtra]:
        """Lista balances pendientes o parciales de un curso."""
        query = select(BalanceCursoExtra).join(
            InscripcionCursoExtra,
            InscripcionCursoExtra.id == BalanceCursoExtra.inscripcion_curso_extra_id
        ).where(
            and_(
                InscripcionCursoExtra.curso_extra_id == curso_id,
                BalanceCursoExtra.estado.in_([EstadoBalance.PENDIENTE, EstadoBalance.PARCIAL])
            )
        ).options(
            joinedload(BalanceCursoExtra.inscripcion)
        )

        result = await self.session.execute(query)
        return result.unique().scalars().all()

    async def listar_por_estado(
        self,
        estado: EstadoBalance,
        sede_id: Optional[int] = None
    ) -> List[BalanceCursoExtra]:
        """Lista balances por estado."""
        query = select(BalanceCursoExtra).where(
            BalanceCursoExtra.estado == estado
        )

        if sede_id is not None:
            query = query.join(
                InscripcionCursoExtra,
                InscripcionCursoExtra.id == BalanceCursoExtra.inscripcion_curso_extra_id
            ).join(
                # Asumiendo que existe relación con CursoExtra
                InscripcionCursoExtra.curso
            ).where(
                InscripcionCursoExtra.curso.sede_id == sede_id
            )

        result = await self.session.execute(query)
        return result.scalars().all()

    async def calcular_total_pendiente(self, curso_id: int) -> Decimal:
        """Suma el total de saldos pendientes de un curso."""
        query = select(
            func.sum(BalanceCursoExtra.saldo)
        ).join(
            InscripcionCursoExtra,
            InscripcionCursoExtra.id == BalanceCursoExtra.inscripcion_curso_extra_id
        ).where(
            and_(
                InscripcionCursoExtra.curso_extra_id == curso_id,
                BalanceCursoExtra.estado.in_([EstadoBalance.PENDIENTE, EstadoBalance.PARCIAL])
            )
        )

        result = await self.session.execute(query)
        return result.scalar() or Decimal('0.00')

    async def calcular_total_pagado(self, curso_id: int) -> Decimal:
        """Suma el total de montos pagados de un curso."""
        query = select(
            func.sum(BalanceCursoExtra.monto_pagado)
        ).join(
            InscripcionCursoExtra,
            InscripcionCursoExtra.id == BalanceCursoExtra.inscripcion_curso_extra_id
        ).where(
            InscripcionCursoExtra.curso_extra_id == curso_id
        )

        result = await self.session.execute(query)
        return result.scalar() or Decimal('0.00')

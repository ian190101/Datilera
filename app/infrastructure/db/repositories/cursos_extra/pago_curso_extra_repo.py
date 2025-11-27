"""
Repositorio para operaciones de Pagos de Cursos Extra.
"""
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from typing import List, Optional
from datetime import date
from decimal import Decimal

from app.infrastructure.db.repositories.base import BaseRepository
from app.infrastructure.db.models.cursos_extra import (
    PagoCursoExtra,
    MetodoPagoCursoExtra,
    BalanceCursoExtra,
    InscripcionCursoExtra
)


class PagoCursoExtraRepository(BaseRepository[PagoCursoExtra]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, PagoCursoExtra)

    async def listar_por_balance(
        self,
        balance_id: int
    ) -> List[PagoCursoExtra]:
        """Lista todos los pagos de un balance."""
        query = select(PagoCursoExtra).where(
            PagoCursoExtra.balance_curso_extra_id == balance_id
        ).order_by(PagoCursoExtra.fecha_pago.desc())

        result = await self.session.execute(query)
        return result.scalars().all()

    async def listar_por_curso(
        self,
        curso_id: int,
        fecha_desde: Optional[date] = None,
        fecha_hasta: Optional[date] = None,
        limite: int = 100,
        offset: int = 0
    ) -> List[PagoCursoExtra]:
        """Lista pagos de un curso con filtro de fechas opcional."""
        query = select(PagoCursoExtra).join(
            BalanceCursoExtra,
            BalanceCursoExtra.id == PagoCursoExtra.balance_curso_extra_id
        ).join(
            InscripcionCursoExtra,
            InscripcionCursoExtra.id == BalanceCursoExtra.inscripcion_curso_extra_id
        ).where(
            InscripcionCursoExtra.curso_extra_id == curso_id
        )

        if fecha_desde is not None:
            query = query.where(PagoCursoExtra.fecha_pago >= fecha_desde)

        if fecha_hasta is not None:
            query = query.where(PagoCursoExtra.fecha_pago <= fecha_hasta)

        query = query.order_by(
            PagoCursoExtra.fecha_pago.desc()
        ).limit(limite).offset(offset)

        result = await self.session.execute(query)
        return result.scalars().all()

    async def listar_por_fecha(
        self,
        fecha_desde: date,
        fecha_hasta: date,
        sede_id: Optional[int] = None
    ) -> List[PagoCursoExtra]:
        """Lista pagos en un rango de fechas."""
        query = select(PagoCursoExtra).where(
            and_(
                PagoCursoExtra.fecha_pago >= fecha_desde,
                PagoCursoExtra.fecha_pago <= fecha_hasta
            )
        )

        if sede_id is not None:
            # Join con inscripcion -> curso -> sede
            query = query.join(
                BalanceCursoExtra,
                BalanceCursoExtra.id == PagoCursoExtra.balance_curso_extra_id
            ).join(
                InscripcionCursoExtra,
                InscripcionCursoExtra.id == BalanceCursoExtra.inscripcion_curso_extra_id
            ).join(
                InscripcionCursoExtra.curso
            ).where(
                InscripcionCursoExtra.curso.sede_id == sede_id
            )

        query = query.order_by(PagoCursoExtra.fecha_pago.desc())

        result = await self.session.execute(query)
        return result.scalars().all()

    async def calcular_total_por_balance(self, balance_id: int) -> Decimal:
        """Suma el total de pagos de un balance."""
        query = select(
            func.sum(PagoCursoExtra.monto)
        ).where(
            PagoCursoExtra.balance_curso_extra_id == balance_id
        )

        result = await self.session.execute(query)
        return result.scalar() or Decimal('0.00')

    async def calcular_total_por_curso(
        self,
        curso_id: int,
        fecha_desde: Optional[date] = None,
        fecha_hasta: Optional[date] = None
    ) -> Decimal:
        """Suma el total de pagos de un curso."""
        query = select(
            func.sum(PagoCursoExtra.monto)
        ).join(
            BalanceCursoExtra,
            BalanceCursoExtra.id == PagoCursoExtra.balance_curso_extra_id
        ).join(
            InscripcionCursoExtra,
            InscripcionCursoExtra.id == BalanceCursoExtra.inscripcion_curso_extra_id
        ).where(
            InscripcionCursoExtra.curso_extra_id == curso_id
        )

        if fecha_desde is not None:
            query = query.where(PagoCursoExtra.fecha_pago >= fecha_desde)

        if fecha_hasta is not None:
            query = query.where(PagoCursoExtra.fecha_pago <= fecha_hasta)

        result = await self.session.execute(query)
        return result.scalar() or Decimal('0.00')

    async def listar_por_metodo_pago(
        self,
        metodo: MetodoPagoCursoExtra,
        sede_id: Optional[int] = None,
        fecha_desde: Optional[date] = None,
        fecha_hasta: Optional[date] = None
    ) -> List[PagoCursoExtra]:
        """Lista pagos por método de pago."""
        query = select(PagoCursoExtra).where(
            PagoCursoExtra.metodo_pago == metodo
        )

        if fecha_desde is not None:
            query = query.where(PagoCursoExtra.fecha_pago >= fecha_desde)

        if fecha_hasta is not None:
            query = query.where(PagoCursoExtra.fecha_pago <= fecha_hasta)

        if sede_id is not None:
            query = query.join(
                BalanceCursoExtra,
                BalanceCursoExtra.id == PagoCursoExtra.balance_curso_extra_id
            ).join(
                InscripcionCursoExtra,
                InscripcionCursoExtra.id == BalanceCursoExtra.inscripcion_curso_extra_id
            ).join(
                InscripcionCursoExtra.curso
            ).where(
                InscripcionCursoExtra.curso.sede_id == sede_id
            )

        query = query.order_by(PagoCursoExtra.fecha_pago.desc())

        result = await self.session.execute(query)
        return result.scalars().all()

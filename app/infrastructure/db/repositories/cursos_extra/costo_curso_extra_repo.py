"""
Repositorio para operaciones de Costos/Gastos de Cursos Extra.
"""
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from typing import List, Optional
from datetime import datetime
from decimal import Decimal

from app.infrastructure.db.repositories.base import BaseRepository
from app.infrastructure.db.models.cursos_extra import CostoCursoExtra


class CostoCursoExtraRepository(BaseRepository[CostoCursoExtra]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, CostoCursoExtra)

    async def listar_por_curso(
        self,
        curso_id: int,
        fecha_desde: Optional[datetime] = None,
        fecha_hasta: Optional[datetime] = None,
        limite: int = 100,
        offset: int = 0
    ) -> List[CostoCursoExtra]:
        """Lista costos de un curso con filtro de fechas opcional."""
        query = select(CostoCursoExtra).where(
            CostoCursoExtra.curso_extra_id == curso_id
        )

        if fecha_desde is not None:
            query = query.where(CostoCursoExtra.fecha_gasto >= fecha_desde)

        if fecha_hasta is not None:
            query = query.where(CostoCursoExtra.fecha_gasto <= fecha_hasta)

        query = query.options(
            joinedload(CostoCursoExtra.categoria)
        ).order_by(
            CostoCursoExtra.fecha_gasto.desc()
        ).limit(limite).offset(offset)

        result = await self.session.execute(query)
        return result.unique().scalars().all()

    async def listar_por_categoria(
        self,
        categoria_id: int,
        limite: int = 100,
        offset: int = 0
    ) -> List[CostoCursoExtra]:
        """Lista costos de una categoría."""
        query = select(CostoCursoExtra).where(
            CostoCursoExtra.categoria_costo_id == categoria_id
        ).order_by(
            CostoCursoExtra.fecha_gasto.desc()
        ).limit(limite).offset(offset)

        result = await self.session.execute(query)
        return result.scalars().all()

    async def calcular_total_por_curso(self, curso_id: int) -> Decimal:
        """Suma el total de costos de un curso."""
        query = select(
            func.sum(CostoCursoExtra.monto)
        ).where(
            CostoCursoExtra.curso_extra_id == curso_id
        )

        result = await self.session.execute(query)
        return result.scalar() or Decimal('0.00')

    async def calcular_total_por_categoria(
        self,
        curso_id: int,
        categoria_id: int
    ) -> Decimal:
        """Suma costos por categoría en un curso."""
        query = select(
            func.sum(CostoCursoExtra.monto)
        ).where(
            and_(
                CostoCursoExtra.curso_extra_id == curso_id,
                CostoCursoExtra.categoria_costo_id == categoria_id
            )
        )

        result = await self.session.execute(query)
        return result.scalar() or Decimal('0.00')

    async def listar_por_rango_fechas(
        self,
        fecha_desde: datetime,
        fecha_hasta: datetime,
        curso_id: Optional[int] = None
    ) -> List[CostoCursoExtra]:
        """Lista costos en un rango de fechas."""
        query = select(CostoCursoExtra).where(
            and_(
                CostoCursoExtra.fecha_gasto >= fecha_desde,
                CostoCursoExtra.fecha_gasto <= fecha_hasta
            )
        )

        if curso_id is not None:
            query = query.where(CostoCursoExtra.curso_extra_id == curso_id)

        query = query.order_by(CostoCursoExtra.fecha_gasto.desc())

        result = await self.session.execute(query)
        return result.scalars().all()

    async def obtener_con_detalles(self, costo_id: int) -> Optional[CostoCursoExtra]:
        """Obtiene un costo con sus relaciones cargadas."""
        query = select(CostoCursoExtra).where(
            CostoCursoExtra.id == costo_id
        ).options(
            joinedload(CostoCursoExtra.categoria),
            joinedload(CostoCursoExtra.curso)
        )

        result = await self.session.execute(query)
        return result.unique().scalar_one_or_none()

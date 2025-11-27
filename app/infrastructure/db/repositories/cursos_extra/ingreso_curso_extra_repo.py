"""
Repositorio para operaciones de Ingresos Consolidados de Cursos Extra.
"""
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, Dict
from decimal import Decimal

from app.infrastructure.db.repositories.base import BaseRepository
from app.infrastructure.db.models.cursos_extra import IngresoCursoExtra, CursoExtra


class IngresoCursoExtraRepository(BaseRepository[IngresoCursoExtra]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, IngresoCursoExtra)

    async def obtener_por_curso(self, curso_id: int) -> Optional[IngresoCursoExtra]:
        """Obtiene el registro de ingresos de un curso."""
        query = select(IngresoCursoExtra).where(
            IngresoCursoExtra.curso_extra_id == curso_id
        )

        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def actualizar_ingresos(
        self,
        curso_id: int,
        total_ingresos: Decimal
    ) -> Optional[IngresoCursoExtra]:
        """Actualiza el total de ingresos."""
        query = update(IngresoCursoExtra).where(
            IngresoCursoExtra.curso_extra_id == curso_id
        ).values(
            total_ingresos=total_ingresos
        ).returning(IngresoCursoExtra)

        result = await self.session.execute(query)
        await self.session.commit()
        return result.scalar_one_or_none()

    async def actualizar_gastos(
        self,
        curso_id: int,
        total_gastos: Decimal
    ) -> Optional[IngresoCursoExtra]:
        """Actualiza el total de gastos."""
        query = update(IngresoCursoExtra).where(
            IngresoCursoExtra.curso_extra_id == curso_id
        ).values(
            total_gastos=total_gastos
        ).returning(IngresoCursoExtra)

        result = await self.session.execute(query)
        await self.session.commit()
        return result.scalar_one_or_none()

    async def recalcular_ganancias(self, curso_id: int) -> Optional[IngresoCursoExtra]:
        """
        Recalcula ganancia_bruta, ganancia_institucion y ganancia_instructor
        basándose en los valores actuales de ingresos, gastos y el porcentaje del curso.
        """
        # Obtener el registro de ingresos
        ingreso = await self.obtener_por_curso(curso_id)
        if not ingreso:
            return None

        # Obtener el porcentaje de la institución del curso
        query_curso = select(CursoExtra.porcentaje_institucion).where(
            CursoExtra.id == curso_id
        )
        result_curso = await self.session.execute(query_curso)
        porcentaje_institucion = result_curso.scalar_one_or_none()

        if porcentaje_institucion is None:
            return None

        # Calcular ganancias
        ganancia_bruta = ingreso.total_ingresos - ingreso.total_gastos
        ganancia_institucion = (ganancia_bruta * porcentaje_institucion) / Decimal('100')
        ganancia_instructor = ganancia_bruta - ganancia_institucion

        # Actualizar
        query = update(IngresoCursoExtra).where(
            IngresoCursoExtra.curso_extra_id == curso_id
        ).values(
            ganancia_bruta=ganancia_bruta,
            ganancia_institucion=ganancia_institucion,
            ganancia_instructor=ganancia_instructor
        ).returning(IngresoCursoExtra)

        result = await self.session.execute(query)
        await self.session.commit()
        return result.scalar_one_or_none()

    async def obtener_balance_curso(self, curso_id: int) -> Dict:
        """
        Retorna un diccionario con el balance completo del curso.
        """
        ingreso = await self.obtener_por_curso(curso_id)
        
        if not ingreso:
            return {
                'total_ingresos': Decimal('0.00'),
                'total_gastos': Decimal('0.00'),
                'ganancia_bruta': Decimal('0.00'),
                'ganancia_institucion': Decimal('0.00'),
                'ganancia_instructor': Decimal('0.00'),
                'porcentaje_institucion': Decimal('0.00')
            }

        # Obtener el porcentaje del curso
        query_curso = select(CursoExtra.porcentaje_institucion).where(
            CursoExtra.id == curso_id
        )
        result_curso = await self.session.execute(query_curso)
        porcentaje_institucion = result_curso.scalar_one_or_none() or Decimal('0.00')

        return {
            'total_ingresos': ingreso.total_ingresos,
            'total_gastos': ingreso.total_gastos,
            'ganancia_bruta': ingreso.ganancia_bruta,
            'ganancia_institucion': ingreso.ganancia_institucion,
            'ganancia_instructor': ingreso.ganancia_instructor,
            'porcentaje_institucion': porcentaje_institucion
        }

    async def actualizar_completo(
        self,
        curso_id: int,
        total_ingresos: Decimal,
        total_gastos: Decimal
    ) -> Optional[IngresoCursoExtra]:
        """
        Actualiza ingresos, gastos y recalcula todas las ganancias en una sola operación.
        """
        # Obtener porcentaje de la institución
        query_curso = select(CursoExtra.porcentaje_institucion).where(
            CursoExtra.id == curso_id
        )
        result_curso = await self.session.execute(query_curso)
        porcentaje_institucion = result_curso.scalar_one_or_none()

        if porcentaje_institucion is None:
            return None

        # Calcular ganancias
        ganancia_bruta = total_ingresos - total_gastos
        ganancia_institucion = (ganancia_bruta * porcentaje_institucion) / Decimal('100')
        ganancia_instructor = ganancia_bruta - ganancia_institucion

        # Actualizar todo
        query = update(IngresoCursoExtra).where(
            IngresoCursoExtra.curso_extra_id == curso_id
        ).values(
            total_ingresos=total_ingresos,
            total_gastos=total_gastos,
            ganancia_bruta=ganancia_bruta,
            ganancia_institucion=ganancia_institucion,
            ganancia_instructor=ganancia_instructor
        ).returning(IngresoCursoExtra)

        result = await self.session.execute(query)
        await self.session.commit()
        return result.scalar_one_or_none()

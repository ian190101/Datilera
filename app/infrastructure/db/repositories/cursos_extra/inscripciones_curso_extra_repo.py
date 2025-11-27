"""
Repositorio para operaciones de Inscripciones a Cursos Extra.
"""
from sqlalchemy import select, and_, func, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from typing import List, Optional

from app.infrastructure.db.repositories.base import BaseRepository
from app.infrastructure.db.models.cursos_extra import (
    InscripcionCursoExtra,
    EstadoInscripcionCursoExtra,
    TipoAlumnoCursoExtra
)


class InscripcionCursoExtraRepository(BaseRepository[InscripcionCursoExtra]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, InscripcionCursoExtra)

    async def obtener_por_curso(
        self,
        curso_id: int,
        estado: Optional[EstadoInscripcionCursoExtra] = None,
        limite: int = 100,
        offset: int = 0
    ) -> List[InscripcionCursoExtra]:
        """Lista inscripciones de un curso."""
        query = select(InscripcionCursoExtra).where(
            InscripcionCursoExtra.curso_extra_id == curso_id
        )

        if estado is not None:
            query = query.where(InscripcionCursoExtra.estado == estado)

        query = query.order_by(
            InscripcionCursoExtra.fecha_inscripcion.desc()
        ).limit(limite).offset(offset)

        result = await self.session.execute(query)
        return result.scalars().all()

    async def obtener_por_alumno_interno(
        self,
        alumno_id: int,
        estado: Optional[EstadoInscripcionCursoExtra] = None
    ) -> List[InscripcionCursoExtra]:
        """Lista inscripciones de un alumno interno."""
        query = select(InscripcionCursoExtra).where(
            InscripcionCursoExtra.alumno_id == alumno_id
        )

        if estado is not None:
            query = query.where(InscripcionCursoExtra.estado == estado)

        query = query.order_by(InscripcionCursoExtra.fecha_inscripcion.desc())

        result = await self.session.execute(query)
        return result.scalars().all()

    async def obtener_por_alumno_externo(
        self,
        alumno_externo_id: int,
        estado: Optional[EstadoInscripcionCursoExtra] = None
    ) -> List[InscripcionCursoExtra]:
        """Lista inscripciones de un alumno externo."""
        query = select(InscripcionCursoExtra).where(
            InscripcionCursoExtra.alumno_externo_id == alumno_externo_id
        )

        if estado is not None:
            query = query.where(InscripcionCursoExtra.estado == estado)

        query = query.order_by(InscripcionCursoExtra.fecha_inscripcion.desc())

        result = await self.session.execute(query)
        return result.scalars().all()

    async def actualizar_estado(
        self,
        inscripcion_id: int,
        estado: EstadoInscripcionCursoExtra
    ) -> Optional[InscripcionCursoExtra]:
        """Actualiza el estado de una inscripción."""
        query = update(InscripcionCursoExtra).where(
            InscripcionCursoExtra.id == inscripcion_id
        ).values(estado=estado).returning(InscripcionCursoExtra)

        result = await self.session.execute(query)
        await self.session.commit()
        return result.scalar_one_or_none()

    async def existe_inscripcion_activa(
        self,
        curso_id: int,
        alumno_id: Optional[int] = None,
        alumno_externo_id: Optional[int] = None
    ) -> bool:
        """Verifica si existe una inscripción activa."""
        conditions = [
            InscripcionCursoExtra.curso_extra_id == curso_id,
            InscripcionCursoExtra.estado == EstadoInscripcionCursoExtra.ACTIVO
        ]

        if alumno_id is not None:
            conditions.append(InscripcionCursoExtra.alumno_id == alumno_id)

        if alumno_externo_id is not None:
            conditions.append(InscripcionCursoExtra.alumno_externo_id == alumno_externo_id)

        query = select(InscripcionCursoExtra).where(and_(*conditions))

        result = await self.session.execute(query)
        return result.scalar_one_or_none() is not None

    async def contar_inscritos_activos(self, curso_id: int) -> int:
        """Cuenta inscripciones activas de un curso."""
        query = select(func.count(InscripcionCursoExtra.id)).where(
            and_(
                InscripcionCursoExtra.curso_extra_id == curso_id,
                InscripcionCursoExtra.estado == EstadoInscripcionCursoExtra.ACTIVO
            )
        )

        result = await self.session.execute(query)
        return result.scalar() or 0

    async def contar_por_tipo(
        self,
        curso_id: int,
        tipo: TipoAlumnoCursoExtra
    ) -> int:
        """Cuenta inscripciones por tipo (internos/externos)."""
        query = select(func.count(InscripcionCursoExtra.id)).where(
            and_(
                InscripcionCursoExtra.curso_extra_id == curso_id,
                InscripcionCursoExtra.tipo_alumno == tipo,
                InscripcionCursoExtra.estado == EstadoInscripcionCursoExtra.ACTIVO
            )
        )

        result = await self.session.execute(query)
        return result.scalar() or 0

    async def listar_con_detalles(
        self,
        curso_id: int,
        limite: int = 100,
        offset: int = 0
    ) -> List[InscripcionCursoExtra]:
        """Lista inscripciones con eager loading de relaciones."""
        query = select(InscripcionCursoExtra).where(
            InscripcionCursoExtra.curso_extra_id == curso_id
        ).options(
            joinedload(InscripcionCursoExtra.alumno),
            joinedload(InscripcionCursoExtra.alumno_externo),
            joinedload(InscripcionCursoExtra.balance)
        ).order_by(
            InscripcionCursoExtra.fecha_inscripcion.desc()
        ).limit(limite).offset(offset)

        result = await self.session.execute(query)
        return result.unique().scalars().all()

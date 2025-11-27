"""
Repositorio para operaciones de Alumnos Externos.
"""
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.infrastructure.db.repositories.base import BaseRepository
from app.infrastructure.db.models.cursos_extra import AlumnoExterno


class AlumnoExternoRepository(BaseRepository[AlumnoExterno]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, AlumnoExterno)

    async def obtener_por_sede(
        self,
        sede_id: int,
        limite: int = 100,
        offset: int = 0
    ) -> List[AlumnoExterno]:
        """Lista alumnos externos de una sede."""
        query = select(AlumnoExterno).where(
            AlumnoExterno.sede_id == sede_id
        ).order_by(
            AlumnoExterno.nombre_completo
        ).limit(limite).offset(offset)

        result = await self.session.execute(query)
        return result.scalars().all()

    async def buscar_por_nombre(
        self,
        nombre: str,
        sede_id: Optional[int] = None,
        limite: int = 20
    ) -> List[AlumnoExterno]:
        """Busca alumnos externos por nombre."""
        query = select(AlumnoExterno).where(
            AlumnoExterno.nombre_completo.ilike(f"%{nombre}%")
        )

        if sede_id is not None:
            query = query.where(AlumnoExterno.sede_id == sede_id)

        query = query.order_by(AlumnoExterno.nombre_completo).limit(limite)

        result = await self.session.execute(query)
        return result.scalars().all()

    async def buscar_por_celular_tutor(
        self,
        celular: str,
        sede_id: Optional[int] = None
    ) -> List[AlumnoExterno]:
        """Busca alumnos externos por celular del tutor."""
        query = select(AlumnoExterno).where(
            AlumnoExterno.tutor_celular.like(f"%{celular}%")
        )

        if sede_id is not None:
            query = query.where(AlumnoExterno.sede_id == sede_id)

        query = query.order_by(AlumnoExterno.nombre_completo)

        result = await self.session.execute(query)
        return result.scalars().all()

    async def existe_por_nombre_y_tutor(
        self,
        nombre_completo: str,
        tutor_celular: str,
        sede_id: int
    ) -> bool:
        """Verifica si existe un alumno externo con ese nombre y tutor."""
        query = select(AlumnoExterno).where(
            and_(
                AlumnoExterno.nombre_completo == nombre_completo,
                AlumnoExterno.tutor_celular == tutor_celular,
                AlumnoExterno.sede_id == sede_id
            )
        )

        result = await self.session.execute(query)
        return result.scalar_one_or_none() is not None

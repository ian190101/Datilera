# app/infrastructure/db/repositories/alumnos/alumnos_hermanos_repo.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.infrastructure.db.models.alumnos.alumnos_hermanos import AlumnoHermano


class AlumnosHermanosRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def crear(self, data: dict) -> AlumnoHermano:
        """Crear un nuevo registro de hermano"""
        hermano = AlumnoHermano(**data)
        self.session.add(hermano)
        await self.session.commit()
        await self.session.refresh(hermano)
        return hermano

    async def obtener_por_id(self, id: int) -> AlumnoHermano:
        """Obtener hermano por ID"""
        result = await self.session.execute(
            select(AlumnoHermano).where(AlumnoHermano.id == id)
        )
        return result.scalar_one_or_none()

    async def listar_por_alumno(self, alumno_id: int):
        """Obtener todos los hermanos de un alumno"""
        result = await self.session.execute(
            select(AlumnoHermano)
            .where(AlumnoHermano.alumno_id == alumno_id)
            .order_by(AlumnoHermano.lugar_ocupa)
        )
        return result.scalars().all()

    async def actualizar(self, id: int, data: dict) -> AlumnoHermano:
        """Actualizar datos de un hermano"""
        hermano = await self.obtener_por_id(id)
        if hermano:
            for key, value in data.items():
                setattr(hermano, key, value)
            await self.session.commit()
            await self.session.refresh(hermano)
        return hermano

    async def eliminar(self, id: int) -> bool:
        """Eliminar un registro de hermano"""
        hermano = await self.obtener_por_id(id)
        if hermano:
            await self.session.delete(hermano)
            await self.session.commit()
            return True
        return False

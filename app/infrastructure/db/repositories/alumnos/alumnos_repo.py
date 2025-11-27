# app/infrastructure/db/repositories/alumnos/alumnos_repo.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.infrastructure.db.models.alumnos.alumnos import Alumno

class AlumnosRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def crear(self, data: dict) -> Alumno:
        alumno = Alumno(**data)
        self.session.add(alumno)
        await self.session.commit()
        await self.session.refresh(alumno)
        return alumno

    async def obtener_por_id(self, id: int) -> Alumno:
        result = await self.session.execute(
            select(Alumno).where(Alumno.id == id)
        )
        return result.scalar_one_or_none()

    async def obtener_por_codigo(self, codigo: str) -> Alumno:
        result = await self.session.execute(
            select(Alumno).where(Alumno.codigo_unico == codigo)
        )
        return result.scalar_one_or_none()

    async def listar_por_tutor(self, tutor_id: int):
        result = await self.session.execute(
            select(Alumno)
            .join(Alumno.tutores)
            .where(Alumno.tutores.any(id=tutor_id))
        )
        return result.scalars().all()

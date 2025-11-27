# app/infrastructure/db/repositories/alumnos/alumnos_tutores_repo.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.infrastructure.db.models.alumnos.alumnos_tutores import AlumnoTutor

class AlumnosTutoresRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def crear(self, data: dict) -> AlumnoTutor:
        obj = AlumnoTutor(**data)
        self.session.add(obj)
        await self.session.commit()
        await self.session.refresh(obj)
        return obj

    async def obtener_por_ids(self, alumno_id: int, tutor_id: int):
        result = await self.session.execute(
            select(AlumnoTutor).where(
                AlumnoTutor.alumno_id == alumno_id,
                AlumnoTutor.tutor_id == tutor_id
            )
        )
        return result.scalar_one_or_none()

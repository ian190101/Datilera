# app/infrastructure/db/repositories/alumnos/tutores_repo.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.infrastructure.db.models.alumnos.tutores import Tutor

class TutoresRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def crear(self, data: dict) -> Tutor:
        obj = Tutor(**data)
        self.session.add(obj)
        await self.session.commit()
        await self.session.refresh(obj)
        return obj

    async def obtener_por_ci(self, ci: str) -> Tutor:
        result = await self.session.execute(
            select(Tutor).where(Tutor.ci_numero == ci)
        )
        return result.scalar_one_or_none()

    async def listar_por_alumno(self, alumno_id: int):
        result = await self.session.execute(
            select(Tutor)
            .join(Tutor.alumnos)
            .where(Tutor.alumnos.any(id=alumno_id))
        )
        return result.scalars().all()

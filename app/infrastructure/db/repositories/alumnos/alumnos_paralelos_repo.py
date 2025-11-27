# app/infrastructure/db/repositories/alumnos/alumnos_paralelos_repo.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.infrastructure.db.models.alumnos.alumnos_paralelos import AlumnoParalelo

class AlumnosParalelosRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def crear(self, data: dict) -> AlumnoParalelo:
        paralelo = AlumnoParalelo(**data)
        self.session.add(paralelo)
        await self.session.commit()
        await self.session.refresh(paralelo)
        return paralelo

    async def obtener_por_id(self, id: int) -> AlumnoParalelo:
        result = await self.session.execute(
            select(AlumnoParalelo).where(AlumnoParalelo.id == id)
        )
        return result.scalar_one_or_none()

    async def listar_por_alumno(self, alumno_id: int):
        result = await self.session.execute(
            select(AlumnoParalelo).where(AlumnoParalelo.alumno_id == alumno_id)
        )
        return result.scalars().all()

    async def listar_por_paralelo(self, paralelo_id: int):
        result = await self.session.execute(
            select(AlumnoParalelo).where(AlumnoParalelo.paralelo_id == paralelo_id)
        )
        return result.scalars().all()

    async def actualizar(self, id: int, data: dict) -> AlumnoParalelo:
        paralelo = await self.obtener_por_id(id)
        if paralelo:
            for key, value in data.items():
                setattr(paralelo, key, value)
            await self.session.commit()
            await self.session.refresh(paralelo)
        return paralelo

    async def eliminar(self, id: int):
        paralelo = await self.obtener_por_id(id)
        if paralelo:
            await self.session.delete(paralelo)
            await self.session.commit()
            return True
        return False

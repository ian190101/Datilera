# app/infrastructure/db/repositories/alumnos/consentimientos_repo.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.infrastructure.db.models.alumnos.consentimientos import Consentimiento


class ConsentimientosRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def crear(self, data: dict) -> Consentimiento:
        """Crear consentimiento para un alumno"""
        consentimiento = Consentimiento(**data)
        self.session.add(consentimiento)
        await self.session.commit()
        await self.session.refresh(consentimiento)
        return consentimiento

    async def obtener_por_alumno(self, alumno_id: int) -> Consentimiento:
        """Obtener consentimiento de un alumno"""
        result = await self.session.execute(
            select(Consentimiento).where(Consentimiento.alumno_id == alumno_id)
        )
        return result.scalar_one_or_none()

    async def actualizar(self, alumno_id: int, data: dict) -> Consentimiento:
        """Actualizar consentimientos"""
        consentimiento = await self.obtener_por_alumno(alumno_id)
        if consentimiento:
            for key, value in data.items():
                setattr(consentimiento, key, value)
            await self.session.commit()
            await self.session.refresh(consentimiento)
        return consentimiento

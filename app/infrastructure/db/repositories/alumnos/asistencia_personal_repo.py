# app/infrastructure/db/repositories/alumnos/asistencia_personal_repo.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_
from app.infrastructure.db.models.alumnos.asistencia_personal import AsistenciaPersonal
from datetime import date


class AsistenciaPersonalRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def crear(self, data: dict) -> AsistenciaPersonal:
        """Registrar entrada/salida de personal"""
        asistencia = AsistenciaPersonal(**data)
        self.session.add(asistencia)
        await self.session.commit()
        await self.session.refresh(asistencia)
        return asistencia

    async def obtener_por_personal_fecha(self, personal_id: int, fecha: date) -> AsistenciaPersonal:
        """Obtener asistencia de personal en una fecha"""
        result = await self.session.execute(
            select(AsistenciaPersonal).where(
                and_(
                    AsistenciaPersonal.personal_id == personal_id,
                    AsistenciaPersonal.fecha == fecha
                )
            )
        )
        return result.scalar_one_or_none()

    async def actualizar(self, id: int, data: dict) -> AsistenciaPersonal:
        """Actualizar registro (ej: hora_salida)"""
        asistencia = await self.obtener_por_id(id)
        if asistencia:
            for key, value in data.items():
                setattr(asistencia, key, value)
            await self.session.commit()
            await self.session.refresh(asistencia)
        return asistencia

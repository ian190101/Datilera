# app/infrastructure/db/repositories/alumnos/asistencia_alumnos_repo.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_
from app.infrastructure.db.models.alumnos.asistencia_alumnos import AsistenciaAlumno
from datetime import date


class AsistenciaAlumnosRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def crear(self, data: dict) -> AsistenciaAlumno:
        """Registrar asistencia de un alumno"""
        asistencia = AsistenciaAlumno(**data)
        self.session.add(asistencia)
        await self.session.commit()
        await self.session.refresh(asistencia)
        return asistencia

    async def obtener_por_id(self, id: int) -> AsistenciaAlumno:
        """Obtener registro de asistencia por ID"""
        result = await self.session.execute(
            select(AsistenciaAlumno).where(AsistenciaAlumno.id == id)
        )
        return result.scalar_one_or_none()

    async def obtener_por_alumno_fecha(self, alumno_id: int, fecha: date) -> AsistenciaAlumno:
        """Obtener asistencia de un alumno en una fecha específica"""
        result = await self.session.execute(
            select(AsistenciaAlumno).where(
                and_(
                    AsistenciaAlumno.alumno_id == alumno_id,
                    AsistenciaAlumno.fecha == fecha
                )
            )
        )
        return result.scalar_one_or_none()

    async def listar_por_alumno(self, alumno_id: int, fecha_desde: date = None, fecha_hasta: date = None):
        """Listar asistencias de un alumno en un rango de fechas"""
        query = select(AsistenciaAlumno).where(AsistenciaAlumno.alumno_id == alumno_id)
        
        if fecha_desde:
            query = query.where(AsistenciaAlumno.fecha >= fecha_desde)
        if fecha_hasta:
            query = query.where(AsistenciaAlumno.fecha <= fecha_hasta)
        
        query = query.order_by(AsistenciaAlumno.fecha.desc())
        
        result = await self.session.execute(query)
        return result.scalars().all()

    async def listar_por_sede_fecha(self, sede_id: int, fecha: date):
        """Listar todas las asistencias de una sede en una fecha"""
        result = await self.session.execute(
            select(AsistenciaAlumno).where(
                and_(
                    AsistenciaAlumno.sede_id == sede_id,
                    AsistenciaAlumno.fecha == fecha
                )
            )
        )
        return result.scalars().all()

    async def actualizar(self, id: int, data: dict) -> AsistenciaAlumno:
        """Actualizar registro de asistencia (ej: agregar hora_retraso)"""
        asistencia = await self.obtener_por_id(id)
        if asistencia:
            for key, value in data.items():
                setattr(asistencia, key, value)
            await self.session.commit()
            await self.session.refresh(asistencia)
        return asistencia

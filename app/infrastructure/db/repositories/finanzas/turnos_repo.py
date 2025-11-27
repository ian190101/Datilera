# app/infrastructure/db/repositories/finanzas/turnos_repo.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_
from app.infrastructure.db.models.finanzas.turnos import Turno
from datetime import date


class TurnosRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def crear(self, data: dict) -> Turno:
        """Crear un nuevo turno"""
        turno = Turno(**data)
        self.session.add(turno)
        await self.session.commit()
        await self.session.refresh(turno)
        return turno

    async def obtener_por_id(self, id: int) -> Turno:
        """Obtener turno por ID"""
        result = await self.session.execute(
            select(Turno).where(Turno.id == id)
        )
        return result.scalar_one_or_none()

    async def obtener_por_nombre(self, nombre: str) -> Turno:
        """Obtener turno por nombre único"""
        result = await self.session.execute(
            select(Turno).where(Turno.nombre == nombre)
        )
        return result.scalar_one_or_none()

    async def listar_por_sede(self, sede_id: int, solo_activos: bool = True):
        """Listar turnos de una sede"""
        query = select(Turno).where(Turno.sede_id == sede_id)
        
        if solo_activos:
            query = query.where(Turno.activo == True)
        
        result = await self.session.execute(query)
        return result.scalars().all()

    async def listar_activos(self):
        """Listar todos los turnos activos (para combos/selects)"""
        result = await self.session.execute(
            select(Turno).where(Turno.activo == True).order_by(Turno.nombre)
        )
        return result.scalars().all()

    async def actualizar(self, id: int, data: dict) -> Turno:
        """Actualizar un turno"""
        turno = await self.obtener_por_id(id)
        if turno:
            for key, value in data.items():
                setattr(turno, key, value)
            await self.session.commit()
            await self.session.refresh(turno)
        return turno

    async def desactivar(self, id: int) -> Turno:
        """Desactivar un turno (soft delete)"""
        turno = await self.obtener_por_id(id)
        if turno:
            turno.activo = False
            await self.session.commit()
            await self.session.refresh(turno)
        return turno

    async def eliminar(self, id: int) -> bool:
        """Eliminar permanentemente un turno (usar con cuidado)"""
        turno = await self.obtener_por_id(id)
        if turno:
            await self.session.delete(turno)
            await self.session.commit()
            return True
        return False

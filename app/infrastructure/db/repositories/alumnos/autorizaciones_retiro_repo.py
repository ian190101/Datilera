# app/infrastructure/db/repositories/alumnos/autorizaciones_retiro_repo.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.infrastructure.db.models.alumnos.autorizaciones_retiro import AutorizacionRetiro


class AutorizacionesRetiroRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def crear(self, data: dict) -> AutorizacionRetiro:
        """Crear nueva autorización de retiro"""
        autorizacion = AutorizacionRetiro(**data)
        self.session.add(autorizacion)
        await self.session.commit()
        await self.session.refresh(autorizacion)
        return autorizacion

    async def obtener_por_id(self, id: int) -> AutorizacionRetiro:
        """Obtener autorización por ID"""
        result = await self.session.execute(
            select(AutorizacionRetiro).where(AutorizacionRetiro.id == id)
        )
        return result.scalar_one_or_none()

    async def listar_por_alumno(self, alumno_id: int, solo_activas: bool = True):
        """Listar autorizaciones de un alumno"""
        query = select(AutorizacionRetiro).where(
            AutorizacionRetiro.alumno_id == alumno_id
        )
        
        if solo_activas:
            query = query.where(AutorizacionRetiro.activo == True)
        
        result = await self.session.execute(query)
        return result.scalars().all()

    async def obtener_por_ci(self, alumno_id: int, ci_numero: str) -> AutorizacionRetiro:
        """Buscar autorización activa por CI"""
        result = await self.session.execute(
            select(AutorizacionRetiro).where(
                AutorizacionRetiro.alumno_id == alumno_id,
                AutorizacionRetiro.ci_numero == ci_numero,
                AutorizacionRetiro.activo == True
            )
        )
        return result.scalar_one_or_none()

    async def desactivar(self, id: int) -> AutorizacionRetiro:
        """Desactivar una autorización"""
        autorizacion = await self.obtener_por_id(id)
        if autorizacion:
            autorizacion.activo = False
            await self.session.commit()
            await self.session.refresh(autorizacion)
        return autorizacion

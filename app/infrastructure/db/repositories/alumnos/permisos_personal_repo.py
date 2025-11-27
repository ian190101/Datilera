# app/infrastructure/db/repositories/alumnos/permisos_personal_repo.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.infrastructure.db.models.alumnos.permisos_personal import PermisoPersonal


class PermisosPersonalRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def crear(self, data: dict) -> PermisoPersonal:
        """Crear solicitud de permiso"""
        permiso = PermisoPersonal(**data)
        self.session.add(permiso)
        await self.session.commit()
        await self.session.refresh(permiso)
        return permiso

    async def listar_por_sede(self, sede_id: int, estado: str = None):
        """Listar permisos de una sede"""
        query = select(PermisoPersonal).where(PermisoPersonal.sede_id == sede_id)
        
        if estado:
            query = query.where(PermisoPersonal.estado == estado)
        
        result = await self.session.execute(query)
        return result.scalars().all()

    async def actualizar_estado(self, id: int, estado: str, aprobado_por_id: int) -> PermisoPersonal:
        """Aprobar o rechazar permiso"""
        permiso = await self.obtener_por_id(id)
        if permiso:
            permiso.estado = estado
            permiso.aprobado_por_id = aprobado_por_id
            await self.session.commit()
            await self.session.refresh(permiso)
        return permiso

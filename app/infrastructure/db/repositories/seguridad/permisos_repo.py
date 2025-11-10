# app/infrastructure/db/repositories/seguridad/permisos_repo.py
from __future__ import annotations
from typing import Optional, Sequence
from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.infrastructure.db.repositories.base import BaseRepository
from app.infrastructure.db.models.seguridad import Permiso as PermisoModel, RolPermiso
from app.kernel.domain.seguridad.permiso_entidad import Permiso, Accion

class PermisosRepository(BaseRepository[PermisoModel]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, PermisoModel)

    def _to_domain(self, m: PermisoModel) -> Permiso:
        return Permiso(recurso=m.vista, accion=Accion(m.accion))

    async def get_by_id(self, permiso_id: int) -> Optional[Permiso]:
        m = await super().get_by_id(permiso_id)
        return self._to_domain(m) if m else None

    async def listar_por_rol(self, rol_id: int) -> Sequence[Permiso]:
        stmt = (
            select(PermisoModel)
            .join(RolPermiso, RolPermiso.permiso_id == PermisoModel.id)
            .where(RolPermiso.rol_id == rol_id)
        )
        res = await self.session.execute(stmt)
        return [self._to_domain(x) for x in res.scalars().all()]

    async def rol_tiene_permiso(self, rol_id: int, permiso_id: int) -> bool:
        stmt = select(RolPermiso).where(
            RolPermiso.rol_id == rol_id, RolPermiso.permiso_id == permiso_id
        ).limit(1)
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none() is not None

    async def asignar_a_rol(self, rol_id: int, permiso_id: int) -> None:
        await self.session.execute(
            insert(RolPermiso).values(rol_id=rol_id, permiso_id=permiso_id)
        )

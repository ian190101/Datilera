# app/infrastructure/db/repositories/seguridad/roles_permiso_repo.py
from __future__ import annotations

from typing import List, Optional
from sqlalchemy import select, insert, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.repositories.base import BaseRepository
from app.infrastructure.db.models.seguridad import RolPermiso as RolPermisoModel
from app.kernel.domain.seguridad.rol_permiso_entidad import RolPermiso


class RolPermisoRepository(BaseRepository[RolPermisoModel]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, RolPermisoModel)

    def _to_domain(self, m: RolPermisoModel) -> RolPermiso:
        return RolPermiso.model_validate(m)

    async def ya_asignado(self, rol_id: int, permiso_id: int) -> bool:
        """Verifica si un permiso ya está asignado a un rol."""
        stmt = (
            select(RolPermisoModel)
            .where(
                RolPermisoModel.rol_id == rol_id,
                RolPermisoModel.permiso_id == permiso_id
            )
            .limit(1)
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none() is not None

    async def asignar(self, rol_id: int, permiso_id: int) -> None:
        """Asigna un permiso a un rol."""
        await self.session.execute(
            insert(RolPermisoModel).values(rol_id=rol_id, permiso_id=permiso_id)
        )

    async def revocar(self, rol_id: int, permiso_id: int) -> bool:
        """Revoca un permiso de un rol. Retorna True si se revocó."""
        stmt = delete(RolPermisoModel).where(
            RolPermisoModel.rol_id == rol_id,
            RolPermisoModel.permiso_id == permiso_id
        )
        result = await self.session.execute(stmt)
        return result.rowcount > 0

    async def get_by_rol_y_permiso(
        self, rol_id: int, permiso_id: int
    ) -> Optional[RolPermiso]:
        """Obtiene la asignación rol-permiso si existe."""
        stmt = (
            select(RolPermisoModel)
            .where(
                RolPermisoModel.rol_id == rol_id,
                RolPermisoModel.permiso_id == permiso_id
            )
            .limit(1)
        )
        res = await self.session.execute(stmt)
        m = res.scalar_one_or_none()
        return self._to_domain(m) if m else None

    async def listar_por_rol(self, rol_id: int) -> List[RolPermiso]:
        """Lista todas las asignaciones de permisos de un rol."""
        stmt = select(RolPermisoModel).where(RolPermisoModel.rol_id == rol_id)
        res = await self.session.execute(stmt)
        return [self._to_domain(m) for m in res.scalars().all()]

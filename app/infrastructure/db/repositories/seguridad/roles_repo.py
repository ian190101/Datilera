# app/infrastructure/db/repositories/seguridad/roles_repo.py
from __future__ import annotations
from typing import Optional, Sequence
from sqlalchemy import select, update, insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.infrastructure.db.repositories.base import BaseRepository
from app.infrastructure.db.models.seguridad import Rol as RolModel, Permiso as PermisoModel
from app.kernel.domain.seguridad.rol_entidad import Rol
from app.kernel.domain.seguridad.permiso_entidad import Permiso, Accion

class RolesRepository(BaseRepository[RolModel]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, RolModel)

    def _to_domain(self, m: RolModel) -> Rol:
        perms = [Permiso(vista=p.vista, accion=Accion(p.accion)) for p in getattr(m, "permisos", [])]
        return Rol(id=m.id, nombre=m.nombre, descripcion=m.descripcion, permisos=perms)

    async def get_by_id(self, rol_id: int) -> Optional[Rol]:
        stmt = select(RolModel).options(selectinload(RolModel.permisos)).where(RolModel.id == rol_id).limit(1)
        res = await self.session.execute(stmt)
        m = res.scalar_one_or_none()
        return self._to_domain(m) if m else None

    async def get_by_nombre(self, nombre: str) -> Optional[Rol]:
        stmt = select(RolModel).options(selectinload(RolModel.permisos)).where(RolModel.nombre == nombre).limit(1)
        res = await self.session.execute(stmt)
        m = res.scalar_one_or_none()
        return self._to_domain(m) if m else None

    async def get_by_nombre_or_id(self, ref: int | str) -> Optional[Rol]:
        if isinstance(ref, int):
            return await self.get_by_id(ref)
        return await self.get_by_nombre(ref)

    async def crear(self, *, nombre: str, descripcion: str | None, creado_en) -> Rol:
        res = await self.session.execute(
            insert(RolModel).values(nombre=nombre, descripcion=descripcion, creado_en=creado_en).returning(RolModel)
        )
        m = res.scalar_one()
        return self._to_domain(m)

    async def actualizar(self, rol_id: int, data: dict) -> None:
        await self.session.execute(update(RolModel).where(RolModel.id == rol_id).values(**data))

    async def listar(self) -> Sequence[Rol]:
        stmt = select(RolModel).options(selectinload(RolModel.permisos)).order_by(RolModel.nombre)
        res = await self.session.execute(stmt)
        return [self._to_domain(m) for m in res.scalars().all()]

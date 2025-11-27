# app/infrastructure/db/repositories/seguridad/usuarios_roles.py
from __future__ import annotations
from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.db.repositories.base import BaseRepository
from app.infrastructure.db.models.seguridad import UsuarioRol

class UsuarioRolRepository(BaseRepository[UsuarioRol]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, UsuarioRol)

    async def ya_asignado(self, usuario_id: int, rol_id: int) -> bool:
        stmt = select(UsuarioRol).where(UsuarioRol.usuario_id == usuario_id, UsuarioRol.rol_id == rol_id).limit(1)
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none() is not None

    async def asignar(self, usuario_id: int, rol_id: int) -> None:
        await self.session.execute(insert(UsuarioRol).values(usuario_id=usuario_id, rol_id=rol_id))

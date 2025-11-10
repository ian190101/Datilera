# app/infrastructure/db/repositories/seguridad/usuarios_repo.py
from __future__ import annotations
from typing import Optional
from sqlalchemy import select, update, insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.infrastructure.db.repositories.base import BaseRepository
from app.infrastructure.db.models.seguridad import Usuario as UsuarioModel, Rol as RolModel, Permiso as PermisoModel, PreferenciaUsuario as PrefModel
from app.kernel.domain.seguridad.user_entidad import Usuario
from app.kernel.domain.seguridad.rol_entidad import Rol
from app.kernel.domain.seguridad.permiso_entidad import Permiso, Accion
from app.kernel.domain.seguridad.preferencias_usuario_entidad import PreferenciasUsuario

class UsuariosRepository(BaseRepository[UsuarioModel]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, UsuarioModel)

    def _to_domain(self, m: UsuarioModel) -> Usuario:
        prefs = None
        if getattr(m, "preferencias", None):
            prefs = PreferenciasUsuario(tema=m.preferencias.tema, notificaciones=m.preferencias.notificaciones_push, idioma=m.preferencias.idioma)
        else:
            prefs = PreferenciasUsuario()
        roles: list[Rol] = []
        for r in getattr(m, "roles", []):
            perms = [Permiso(recurso=p.vista, accion=Accion(p.accion)) for p in getattr(r, "permisos", [])]
            roles.append(Rol(id=r.id, nombre=r.nombre, descripcion=r.descripcion, permisos=perms))
        return Usuario(
            id=m.id,
            nombre_usuario=m.username,
            contrasena=m.hash_password,
            rol=roles[0] if roles else Rol(id=0, nombre="sin-rol", descripcion="", permisos=[]),
            sede_id=m.sede_id,
            activo=m.activo,
            foto_perfil=m.foto_perfil_url,
            preferencias=prefs,
        )

    async def get_by_id(self, user_id: int) -> Optional[Usuario]:
        stmt = (
            select(UsuarioModel)
            .options(
                selectinload(UsuarioModel.roles).selectinload(RolModel.permisos),
                selectinload(UsuarioModel.preferencias),
            )
            .where(UsuarioModel.id == user_id)
            .limit(1)
        )
        res = await self.session.execute(stmt)
        m = res.scalar_one_or_none()
        return self._to_domain(m) if m else None

    async def get_by_username(self, username: str) -> Optional[Usuario]:
        stmt = (
            select(UsuarioModel)
            .options(
                selectinload(UsuarioModel.roles).selectinload(RolModel.permisos),
                selectinload(UsuarioModel.preferencias),
            )
            .where(UsuarioModel.username == username)
            .limit(1)
        )
        res = await self.session.execute(stmt)
        m = res.scalar_one_or_none()
        return self._to_domain(m) if m else None

    async def get_by_email(self, email: str) -> Optional[Usuario]:
        stmt = (
            select(UsuarioModel)
            .options(
                selectinload(UsuarioModel.roles).selectinload(RolModel.permisos),
                selectinload(UsuarioModel.preferencias),
            )
            .where(UsuarioModel.email == email)
            .limit(1)
        )
        res = await self.session.execute(stmt)
        m = res.scalar_one_or_none()
        return self._to_domain(m) if m else None

    async def crear(self, **data) -> Usuario:
        res = await self.session.execute(
            insert(UsuarioModel).values(**data).returning(UsuarioModel)
        )
        m = res.scalar_one()
        return await self.get_by_id(m.id)

    async def actualizar_password(self, usuario_id: int, password_hash: str) -> None:
        await self.session.execute(update(UsuarioModel).where(UsuarioModel.id == usuario_id).values(hash_password=password_hash))

    async def actualizar_perfil(self, usuario_id: int, data: dict) -> None:
        await self.session.execute(update(UsuarioModel).where(UsuarioModel.id == usuario_id).values(**data))

    async def actualizar_preferencias(self, usuario_id: int, data: dict) -> None:
        await self.session.execute(update(PrefModel).where(PrefModel.usuario_id == usuario_id).values(**data))

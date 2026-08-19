# app/infrastructure/db/repositories/seguridad/usuarios_repo.py
from __future__ import annotations

from sqlalchemy import distinct, func, insert, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.infrastructure.db.models.seguridad import Permiso as PermisoModel
from app.infrastructure.db.models.seguridad import PreferenciaUsuario as PrefModel
from app.infrastructure.db.models.seguridad import Rol as RolModel
from app.infrastructure.db.models.seguridad import Sede as SedeModel
from app.infrastructure.db.models.seguridad import Usuario as UsuarioModel
from app.infrastructure.db.repositories.base import BaseRepository
from app.kernel.domain.seguridad.permiso_entidad import Permiso as PermisoEntity
from app.kernel.domain.seguridad.preferencias_usuario_entidad import PreferenciasUsuario
from app.kernel.domain.seguridad.rol_entidad import Rol as RolEntity
from app.kernel.domain.seguridad.user_entidad import Usuario
from app.kernel.domain.seguridad.user_entidad import Usuario as UsuarioEntity


class UsuariosRepository(BaseRepository[UsuarioModel]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, UsuarioModel)

    # =================================================================
    # MAPPER: El puente entre Infraestructura (SQL) y Dominio (Pydantic)
    # Este método vive en Infraestructura porque conoce ambos mundos.
    # =================================================================
    def _to_domain(self, model: UsuarioModel) -> UsuarioEntity:
        if not model:
            return None

        prefs = None
        prefs_db: PrefModel | None = getattr(model, "preferencias", None)

        # Verificamos si la relación 'preferencias' está cargada y no es None
        if prefs_db:
            prefs = PreferenciasUsuario(
                tema=prefs_db.tema,
                notificaciones=prefs_db.notificaciones_push,
                idioma=getattr(prefs_db, "idioma", "es"),
            )
        else:
            prefs = PreferenciasUsuario()

        # 1. Mapear Roles
        roles_db: list[RolModel] = getattr(model, "roles", [])
        roles_dominio = []
        for r in roles_db:
            # 2. Mapear Permisos
            permisos_db: list[PermisoModel] = getattr(r, "permisos", [])
            permisos_dominio = []
            for p in permisos_db:
                # Validamos que el objeto permiso sea compatible
                permisos_dominio.append(PermisoEntity.model_validate(p))

            roles_dominio.append(
                RolEntity(
                    id=r.id, nombre=r.nombre, descripcion=r.descripcion or "", permisos=permisos_dominio
                )
            )

        # --- 3. Obtener nombre de la sede ---
        nombre_sede_str = "Principal"

        # CORRECCIÓN 2: Tipamos explícitamente la variable
        sede_obj: SedeModel | None = getattr(model, "sede", None)

        if sede_obj:
            # Ahora el editor sabe que sede_obj tiene .nombre
            nombre_sede_str = sede_obj.nombre

        # 3. Retornar la Entidad de Dominio Pura
        return UsuarioEntity(
            id=model.id,
            # Aquí solucionamos el conflicto de nombres (username db -> nombre_usuario domain)
            nombre_usuario=model.username,
            nombres=model.nombres,
            apellidos=model.apellidos,
            email=model.email,
            telefono=model.telefono,
            contrasena=model.hash_password,
            activo=model.activo,
            debe_cambiar_password=bool(model.debe_cambiar_password),
            sede_nombre=nombre_sede_str,
            sede_id=model.sede_id,
            roles=roles_dominio,
            foto_perfil=model.foto_perfil_url,
            preferencias=prefs,
        )

    async def get_by_id(self, user_id: int) -> Usuario | None:
        stmt = (
            select(UsuarioModel)
            .options(
                selectinload(UsuarioModel.roles).selectinload(RolModel.permisos),
                selectinload(UsuarioModel.preferencias),
                selectinload(UsuarioModel.sede),
            )
            .where(UsuarioModel.id == user_id)
            .limit(1)
        )
        res = await self.session.execute(stmt)
        m = res.scalar_one_or_none()
        return self._to_domain(m) if m else None

    async def get_by_username(self, username: str) -> Usuario | None:
        stmt = (
            select(UsuarioModel)
            .options(
                selectinload(UsuarioModel.roles).selectinload(RolModel.permisos),
                selectinload(UsuarioModel.preferencias),
                selectinload(UsuarioModel.sede),
            )
            .where(UsuarioModel.username == username)
            .limit(1)
        )
        res = await self.session.execute(stmt)
        m = res.scalar_one_or_none()
        return self._to_domain(m) if m else None

    async def get_by_email(self, email: str) -> Usuario | None:
        stmt = (
            select(UsuarioModel)
            .options(
                selectinload(UsuarioModel.roles).selectinload(RolModel.permisos),
                selectinload(UsuarioModel.preferencias),
                selectinload(UsuarioModel.sede),
            )
            .where(UsuarioModel.email == email)
            .limit(1)
        )
        res = await self.session.execute(stmt)
        m = res.scalar_one_or_none()
        return self._to_domain(m) if m else None

    async def list_paginated(
        self,
        page: int,
        per_page: int,
        sede_id: int | None = None,
        rol_nombre: str | None = None,
        activo: bool | None = None,
        q: str | None = None,
    ) -> tuple[list[Usuario], int]:
        """Lista usuarios con conteo exacto y relaciones cargadas sin N+1."""
        filtros = []
        if sede_id is not None:
            filtros.append(UsuarioModel.sede_id == sede_id)
        if activo is not None:
            filtros.append(UsuarioModel.activo.is_(activo))
        if q:
            patron = f"%{q.strip()}%"
            filtros.append(
                or_(
                    UsuarioModel.username.ilike(patron),
                    UsuarioModel.nombres.ilike(patron),
                    UsuarioModel.apellidos.ilike(patron),
                    UsuarioModel.email.ilike(patron),
                )
            )

        consulta = select(UsuarioModel)
        conteo = select(func.count(distinct(UsuarioModel.id)))
        if rol_nombre:
            consulta = consulta.join(UsuarioModel.roles)
            conteo = conteo.select_from(UsuarioModel).join(UsuarioModel.roles)
            filtros.append(func.upper(RolModel.nombre) == rol_nombre.strip().upper())
        else:
            conteo = conteo.select_from(UsuarioModel)

        consulta = (
            consulta.options(
                selectinload(UsuarioModel.roles).selectinload(RolModel.permisos),
                selectinload(UsuarioModel.preferencias),
                selectinload(UsuarioModel.sede),
            )
            .where(*filtros)
            .order_by(UsuarioModel.id.desc())
            .offset((page - 1) * per_page)
            .limit(per_page)
        )
        conteo = conteo.where(*filtros)

        total = int((await self.session.execute(conteo)).scalar_one())
        modelos = (await self.session.execute(consulta)).unique().scalars().all()
        return [self._to_domain(modelo) for modelo in modelos], total

    async def crear(self, **data) -> Usuario:
        res = await self.session.execute(insert(UsuarioModel).values(**data).returning(UsuarioModel))
        m = res.scalar_one()
        return await self.get_by_id(m.id)

    async def actualizar_password(self, usuario_id: int, password_hash: str) -> None:
        await self.session.execute(
            update(UsuarioModel).where(UsuarioModel.id == usuario_id).values(hash_password=password_hash)
        )

    async def actualizar_perfil(self, usuario_id: int, data: dict) -> None:
        await self.session.execute(update(UsuarioModel).where(UsuarioModel.id == usuario_id).values(**data))

    async def actualizar_preferencias(self, usuario_id: int, data: dict) -> None:
        await self.session.execute(update(PrefModel).where(PrefModel.usuario_id == usuario_id).values(**data))

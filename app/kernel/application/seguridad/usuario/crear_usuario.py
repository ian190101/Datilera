# app/kernel/application/seguridad/usuarios/crear_usuario.py
from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, Field, EmailStr, field_validator

from app.kernel.domain.seguridad.errors import (
    UsuarioYaExiste,
    UsuarioEmailDuplicado,
    RolNoEncontrado,
    SedeNoEncontrada,
    RolNoPermitidoParaCreacion,
)
from app.kernel.domain.seguridad.ports import (
    AbstractUserRepository,
    AbstractRolRepository,
    AbstractSedeRepository,
    AbstractUsuarioRolRepository,
    AbstractHasher,
)

# Roles permitidos para creación manual
ROLES_PERMITIDOS = {"SUPERADMIN", "ADMIN"}


class CrearUsuarioDTO(BaseModel):
    username: str = Field(..., min_length=4, max_length=64)
    password: str = Field(..., min_length=8, max_length=128)
    nombre_completo: str = Field(..., max_length=160)
    email: Optional[str] = Field(None, max_length=120)
    telefono: Optional[str] = Field(None, max_length=20)
    rol_nombre: str = Field(..., description="SUPERADMIN o ADMIN")
    sede_id: Optional[int] = Field(None, gt=0, description="Requerido si rol=ADMIN")

    @field_validator("username")
    @classmethod
    def _norm_username(cls, v: str) -> str:
        nv = v.strip().lower()
        if not nv:
            raise ValueError("El username no puede estar vacío")
        return nv

    @field_validator("rol_nombre")
    @classmethod
    def _norm_rol(cls, v: str) -> str:
        return v.strip().upper()


class CrearUsuario:
    """Caso de uso: Crear usuario SuperAdmin o Admin manualmente."""

    def __init__(
        self,
        usuario_repo: AbstractUserRepository,
        rol_repo: AbstractRolRepository,
        sede_repo: AbstractSedeRepository,
        usuario_rol_repo: AbstractUsuarioRolRepository,
        hasher: AbstractHasher,
    ):
        self.usuario_repo = usuario_repo
        self.rol_repo = rol_repo
        self.sede_repo = sede_repo
        self.usuario_rol_repo = usuario_rol_repo
        self.hasher = hasher

    async def execute(self, dto: CrearUsuarioDTO) -> dict:
        # 1) Validar que el rol sea permitido
        if dto.rol_nombre not in ROLES_PERMITIDOS:
            raise RolNoPermitidoParaCreacion(
                f"Solo se pueden crear usuarios con roles: {', '.join(ROLES_PERMITIDOS)}"
            )

        # 2) Validar username único
        existente = await self.usuario_repo.get_by_username(dto.username)
        if existente:
            raise UsuarioYaExiste(f"El username '{dto.username}' ya existe")

        # 3) Validar email único si se proporciona
        if dto.email:
            existente_email = await self.usuario_repo.get_by_email(dto.email)
            if existente_email:
                raise UsuarioEmailDuplicado(f"El email '{dto.email}' ya está registrado")

        # 4) Validar que el rol exista
        rol = await self.rol_repo.get_by_nombre(dto.rol_nombre)
        if not rol:
            raise RolNoEncontrado(f"Rol '{dto.rol_nombre}' no encontrado")

        # 5) Validar sede si es ADMIN
        if dto.rol_nombre == "ADMIN":
            if not dto.sede_id:
                raise ValueError("Se requiere sede_id para crear usuarios con rol ADMIN")
            sede_existe = await self.sede_repo.exists(dto.sede_id)
            if not sede_existe:
                raise SedeNoEncontrada(f"Sede con ID {dto.sede_id} no encontrada")
        else:
            # SUPERADMIN: asignar sede_id = 1 (sede principal) o null según diseño
            dto.sede_id = 1  # O manejar lógica de sede global

        # 6) Hashear contraseña
        password_hash = self.hasher.hash_password(dto.password)

        # 7) Crear usuario
        usuario = await self.usuario_repo.crear(
            username=dto.username,
            hash_password=password_hash,
            nombre_completo=dto.nombre_completo,
            email=dto.email,
            telefono=dto.telefono,
            sede_id=dto.sede_id,
            activo=True,
        )

        # 8) Asignar rol
        await self.usuario_rol_repo.asignar(usuario.id, rol.id)

        return {
            "id": usuario.id,
            "username": dto.username,
            "nombre_completo": dto.nombre_completo,
            "rol": dto.rol_nombre,
            "sede_id": dto.sede_id,
        }

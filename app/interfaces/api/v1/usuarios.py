# app/interfaces/api/v1/usuarios.py
from datetime import UTC, datetime
import secrets
import string

from fastapi import APIRouter, Depends, Query, Body, HTTPException
from starlette import status
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.session import get_session
from app.infrastructure.db.repositories.seguridad.usuarios_repo import UsuariosRepository
from app.infrastructure.db.repositories.seguridad.roles_repo import RolesRepository
from app.infrastructure.db.repositories.seguridad.sede_repo import SedeRepository
from app.infrastructure.db.repositories.seguridad.usuarios_roles_repo import UsuarioRolRepository
from app.infrastructure.auth.auth_utils import PasslibHasher
from app.infrastructure.db.models.seguridad.usuarios import Usuario as UsuarioModel
from app.infrastructure.db.repositories.seguridad.sesiones_repo import SesionesRepository
from app.middleware.api_auth import AuthPrincipal, get_current_principal

from app.kernel.application.seguridad.usuario.crear_usuario import CrearUsuario, CrearUsuarioDTO
from app.kernel.application.seguridad.usuario.actualizar_usuario import EditarUsuario, EditarUsuarioDTO
from app.kernel.application.seguridad.usuario.cambiar_estado_usuario import (
    CambiarEstadoUsuario,
    CambiarEstadoUsuarioDTO,
)
from app.kernel.application.seguridad.usuario.listar_usuarios import ListarUsuarios, ListarUsuariosDTO
from app.kernel.application.seguridad.usuario.obtener_permisos_efectivos import ObtenerPermisosEfectivos

# Para asignar roles a usuarios existentes (no SuperAdmin/Admin)
from app.kernel.application.seguridad.usuario_rol.asignar_rol_usuario import (
    AsignarRolUsuario,
    AsignarRolUsuarioDTO,
)

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])


def generar_password_temporal(longitud: int = 14) -> str:
    """Genera una clave legible pero resistente usando un CSPRNG."""
    if longitud < 12:
        raise ValueError("La contraseña temporal debe tener al menos 12 caracteres")
    obligatorios = [
        secrets.choice(string.ascii_uppercase),
        secrets.choice(string.ascii_lowercase),
        secrets.choice(string.digits),
        secrets.choice("!@#$%*-_"),
    ]
    alfabeto = string.ascii_letters + string.digits + "!@#$%*-_"
    caracteres = obligatorios + [secrets.choice(alfabeto) for _ in range(longitud - len(obligatorios))]
    secrets.SystemRandom().shuffle(caracteres)
    return "".join(caracteres)


def get_usuario_repo(session: AsyncSession = Depends(get_session)) -> UsuariosRepository:
    return UsuariosRepository(session)


def get_rol_repo(session: AsyncSession = Depends(get_session)) -> RolesRepository:
    return RolesRepository(session)


def get_sede_repo(session: AsyncSession = Depends(get_session)) -> SedeRepository:
    return SedeRepository(session)


def get_usuario_rol_repo(session: AsyncSession = Depends(get_session)) -> UsuarioRolRepository:
    return UsuarioRolRepository(session)


def get_hasher() -> PasslibHasher:
    return PasslibHasher()


@router.post("", status_code=status.HTTP_201_CREATED)
async def crear_usuario(
    payload: CrearUsuarioDTO = Body(...),
    usuario_repo: UsuariosRepository = Depends(get_usuario_repo),
    rol_repo: RolesRepository = Depends(get_rol_repo),
    sede_repo: SedeRepository = Depends(get_sede_repo),
    usuario_rol_repo: UsuarioRolRepository = Depends(get_usuario_rol_repo),
    hasher: PasslibHasher = Depends(get_hasher),
):
    """
    Crear usuario SuperAdmin o Admin manualmente.
    
    Restricciones:
    - Solo permite roles: SUPERADMIN, ADMIN
    - SuperAdmin: sede_id opcional (puede gestionar todas las sedes)
    - Admin: sede_id obligatorio (vinculado a una sede específica)
    """
    caso = CrearUsuario(usuario_repo, rol_repo, sede_repo, usuario_rol_repo, hasher)
    result = await caso.execute(payload)
    return result


@router.get("")
async def listar_usuarios(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    sede_id: int | None = Query(None, gt=0),
    rol_nombre: str | None = Query(None, max_length=50),
    activo: bool | None = Query(None),
    q: str | None = Query(None, max_length=100),
    usuario_repo: UsuariosRepository = Depends(get_usuario_repo),
):
    """
    Listar usuarios con filtros.
    
    Filtros disponibles:
    - sede_id: Filtrar por sede específica
    - rol_nombre: Filtrar por rol (ej: ADMIN, TUTOR, PROFESORA)
    - activo: Filtrar por estado activo/inactivo
    - q: Búsqueda por nombre o username
    """
    caso = ListarUsuarios(usuario_repo)
    dto = ListarUsuariosDTO(
        page=page,
        per_page=per_page,
        sede_id=sede_id,
        rol_nombre=rol_nombre,
        activo=activo,
        q=q,
    )
    result = await caso.execute(dto)
    return result


@router.put("/{usuario_id}")
async def editar_usuario(
    usuario_id: int,
    payload: EditarUsuarioDTO = Body(...),
    usuario_repo: UsuariosRepository = Depends(get_usuario_repo),
):
    """
    Editar perfil de usuario.
    
    Permite actualizar:
    - nombre_completo
    - email
    - telefono
    - foto_perfil_url
    
    NO permite cambiar:
    - username (identificador único)
    - rol (usar endpoint de asignación de roles)
    - contraseña (usar endpoint específico de cambio de contraseña)
    """
    payload_dict = payload.model_dump()
    payload_dict["usuario_id"] = usuario_id
    caso = EditarUsuario(usuario_repo)
    result = await caso.execute(EditarUsuarioDTO(**payload_dict))
    return result


@router.put("/{usuario_id}/estado")
async def cambiar_estado_usuario(
    usuario_id: int,
    payload: dict = Body(..., example={"activo": True}),
    usuario_repo: UsuariosRepository = Depends(get_usuario_repo),
):
    """
    Activar o desactivar un usuario.
    
    Body:
    {
        "activo": true  // true para activar, false para desactivar
    }
    """
    dto = CambiarEstadoUsuarioDTO(usuario_id=usuario_id, activo=payload["activo"])
    caso = CambiarEstadoUsuario(usuario_repo)
    result = await caso.execute(dto)
    return result


@router.post("/{usuario_id}/resetear-password")
async def resetear_password_usuario(
    usuario_id: int,
    usuario_repo: UsuariosRepository = Depends(get_usuario_repo),
    hasher: PasslibHasher = Depends(get_hasher),
    principal: AuthPrincipal = Depends(get_current_principal),
):
    """Restablece una cuenta y devuelve la clave temporal una sola vez."""
    usuario = await usuario_repo.session.get(UsuarioModel, usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    if usuario.sede_id != principal.sede_id and not principal.puede_acceder_modulo("Sedes", "Seguridad"):
        raise HTTPException(status_code=403, detail="No puede restablecer usuarios de otra sede")

    password_temporal = generar_password_temporal()
    usuario.hash_password = hasher.hash_password(password_temporal)
    usuario.debe_cambiar_password = True
    usuario.password_temporal_generada_en = datetime.now(UTC).replace(tzinfo=None)
    await SesionesRepository(usuario_repo.session).eliminar_todas(usuario_id)
    await usuario_repo.session.commit()
    return {
        "success": True,
        "usuario_id": usuario.id,
        "username": usuario.username,
        "password_temporal": password_temporal,
        "mensaje": "Contraseña temporal generada. El usuario deberá cambiarla al iniciar sesión.",
    }


@router.get("/{usuario_id}/permisos-efectivos")
async def obtener_permisos_efectivos(
    usuario_id: int,
    usuario_repo: UsuariosRepository = Depends(get_usuario_repo),
):
    """
    Obtener todos los permisos efectivos del usuario.
    
    Retorna la lista completa de permisos que el usuario tiene
    a través de todos sus roles asignados (herencia de permisos).
    """
    caso = ObtenerPermisosEfectivos(usuario_repo)
    result = await caso.execute(usuario_id)
    return result


@router.post("/{usuario_id}/roles", status_code=status.HTTP_204_NO_CONTENT)
async def asignar_rol_a_usuario(
    usuario_id: int,
    payload: dict = Body(..., example={"rol_id": 3}),
    usuario_repo: UsuariosRepository = Depends(get_usuario_repo),
    rol_repo: RolesRepository = Depends(get_rol_repo),
    usuario_rol_repo: UsuarioRolRepository = Depends(get_usuario_rol_repo),
):
    """
    Asigna un rol a un usuario existente.
    
    RESTRICCIONES IMPORTANTES:
    - NO permite asignar roles SuperAdmin o Admin (usar POST /usuarios para crearlos)
    - El usuario debe existir previamente
    - El rol no debe estar ya asignado al usuario
    
    Body:
    {
        "rol_id": 3  // ID del rol a asignar (ej: TUTOR, PROFESORA, AUXILIAR)
    }
    
    Nota: Para cambiar de un rol a otro, usar PUT /usuario-roles/cambiar
    """
    dto = AsignarRolUsuarioDTO(usuario_id=usuario_id, rol_id=payload["rol_id"])
    caso = AsignarRolUsuario(usuario_repo, rol_repo, usuario_rol_repo)
    
    # permitir_restringidos=False → NO permite asignar SuperAdmin/Admin
    await caso.execute(dto, permitir_restringidos=False)
    
    return

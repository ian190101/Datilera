from __future__ import annotations

import unicodedata
from dataclasses import dataclass

from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse

from app.config.settings import get_settings
from app.infrastructure.auth.auth_utils import PyJWTTokenService
from app.infrastructure.db.repositories.seguridad.usuarios_repo import UsuariosRepository
from app.infrastructure.db.session import AsyncSessionLocal

PUBLIC_API_PATHS = frozenset(
    {
        "/api/v1/auth/login",
        "/api/v1/auth/refresh",
        "/api/v1/tutores/validar-codigo",
        "/api/v1/tutores/completar-registro",
        "/api/v1/profesoras/validar-codigo",
        "/api/v1/profesoras/completar-registro",
    }
)


@dataclass(frozen=True, slots=True)
class AuthPrincipal:
    usuario_id: int
    sede_id: int
    permisos: frozenset[str]
    roles: frozenset[str] = frozenset()

    def tiene_permiso(self, permiso: str) -> bool:
        return permiso in self.permisos

    def puede_acceder_modulo(self, *aliases: str) -> bool:
        roles_privilegiados = {
            "admin",
            "administrador",
            "dueno",
            "owner",
            "superadmin",
            "superadministrador",
        }
        if {_normalize(rol) for rol in self.roles} & roles_privilegiados:
            return True
        allowed = {_normalize(item) for item in aliases}
        resources = {_normalize(item.split(":", 1)[0]) for item in self.permisos}
        return bool(resources & (allowed | {"admin", "sistema", "*"}))


def _puede_usar_ruta_operativa(principal: AuthPrincipal, path: str, method: str) -> bool:
    """Habilita solo las operaciones propias de los portales profesora/tutor."""
    if path == "/api/v1/usuarios/me" or path.startswith("/api/v1/usuarios/me/"):
        return method.upper() in {"GET", "PATCH"}

    roles = {_normalize(rol) for rol in principal.roles}
    es_profesora = bool(roles & {"profesor", "profesora", "docente"})
    es_tutor = bool(roles & {"tutor", "padre", "madre", "familiar"})
    if not (es_profesora or es_tutor):
        return False

    metodo = method.upper()
    if path in {"/api/v1/grupos", "/api/v1/paralelos"}:
        return metodo == "GET"

    if path == "/api/v1/notificaciones/enviar":
        return es_profesora and metodo == "POST"

    if path == "/api/v1/notificaciones" or path.startswith("/api/v1/notificaciones/"):
        return metodo == "GET" or (metodo == "PATCH" and path.endswith("/leer"))

    if path.startswith("/api/v1/comunicaciones/"):
        return True

    if path.startswith("/api/v1/academico/"):
        # La profesora registra su seguimiento; el tutor solo consulta el suyo.
        return es_profesora or metodo == "GET"

    return False


def _principal_con_acceso_db(principal: AuthPrincipal, user) -> AuthPrincipal:
    """Combina los claims con los roles y permisos actuales de la base."""
    if not user or not user.activo:
        return principal
    roles = frozenset(rol.nombre for rol in user.roles)
    permisos_db = frozenset(
        permiso.nombre_completo
        for rol in user.roles
        for permiso in rol.permisos
        if getattr(permiso, "activo", True)
    )
    return AuthPrincipal(
        usuario_id=principal.usuario_id,
        sede_id=principal.sede_id,
        permisos=principal.permisos | permisos_db,
        roles=principal.roles | roles,
    )


def _normalize(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    return "".join(char for char in normalized if not unicodedata.combining(char)).casefold()


def _extract_token(request: Request) -> tuple[str | None, bool]:
    header = request.headers.get("Authorization", "")
    if header.startswith("Bearer "):
        return header[7:].strip(), False
    return request.cookies.get("accesstoken") or request.cookies.get("access_token"), True


def _decode_principal(token: str) -> AuthPrincipal:
    try:
        payload = PyJWTTokenService().decode_token(token)
        if payload.get("type") != "access":
            raise ValueError("tipo de token incorrecto")
        return AuthPrincipal(
            usuario_id=int(payload["sub"]),
            sede_id=int(payload["sede"]),
            permisos=frozenset(str(item) for item in payload.get("pms", [])),
            roles=frozenset(str(item) for item in payload.get("roles", [])),
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de acceso inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


async def api_auth_middleware(request: Request, call_next):
    path = request.url.path.rstrip("/") or "/"
    if not path.startswith("/api/v1") or path in PUBLIC_API_PATHS:
        return await call_next(request)

    token, from_cookie = _extract_token(request)
    if not token:
        return JSONResponse(status_code=401, content={"detail": "Autenticación requerida"})

    try:
        request.state.auth = _decode_principal(token)
    except HTTPException as exc:
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

    module_aliases = _module_for_path(path)
    if (
        module_aliases
        and not request.state.auth.puede_acceder_modulo(*module_aliases)
        and not _puede_usar_ruta_operativa(request.state.auth, path, request.method)
    ):
        # Las sesiones antiguas pueden no incluir roles o permisos; recuperamos
        # ambos desde la BD solo cuando el token no autoriza la operacion.
        async with AsyncSessionLocal() as session:
            user = await UsuariosRepository(session).get_by_id(request.state.auth.usuario_id)
        request.state.auth = _principal_con_acceso_db(request.state.auth, user)
        if (
            not request.state.auth.puede_acceder_modulo(*module_aliases)
            and not _puede_usar_ruta_operativa(request.state.auth, path, request.method)
        ):
            return JSONResponse(status_code=403, content={"detail": "Permiso insuficiente para este módulo"})

    # Las cookies se protegen también contra solicitudes cross-site con estado.
    if from_cookie and request.method not in {"GET", "HEAD", "OPTIONS"}:
        origin = request.headers.get("origin")
        if origin:
            settings = get_settings()
            same_origin = origin.rstrip("/") == str(request.base_url).rstrip("/")
            if not same_origin and origin.rstrip("/") not in settings.cors_origin_list:
                return JSONResponse(status_code=403, content={"detail": "Origen no permitido"})

    return await call_next(request)


def _module_for_path(path: str) -> tuple[str, ...] | None:
    # El Copilot está disponible para toda sesión autenticada. Las herramientas
    # sensibles aplican autorización específica antes de consultar o escribir.
    if path in {
        "/api/v1/ia/chat",
        "/api/v1/ia/acciones/confirmar",
        "/api/v1/ia/reportes/finanzas.csv",
    }:
        return None
    segment = path.removeprefix("/api/v1/").split("/", 1)[0]
    modules = {
        "finanzas": ("Finanzas",),
        "ingresos": ("Finanzas",),
        "inventario": ("Inventario", "Inventarios"),
        "inventarios": ("Inventario", "Inventarios"),
        "inscripcion": ("Inscripcion", "Inscripciones"),
        "inscripciones": ("Inscripcion", "Inscripciones"),
        "academico": ("Academico",),
        "grupos": ("Academico",),
        "paralelos": ("Academico",),
        "asignaciones": ("Academico",),
        "comunicaciones": ("Comunicaciones",),
        "notificaciones": ("Comunicaciones", "Notificaciones"),
        "usuarios": ("Seguridad", "Usuarios"),
        "seguridad": ("Seguridad",),
        "cursos-extra": ("Cursos Extra", "CursosExtra"),
        "ia": ("IA",),
        "exportacion": ("Exportacion", "Exportaciones"),
        "exportaciones": ("Exportacion", "Exportaciones"),
    }
    return modules.get(segment)


async def get_current_principal(request: Request) -> AuthPrincipal:
    principal = getattr(request.state, "auth", None)
    if principal is None:
        token, _ = _extract_token(request)
        if not token:
            raise HTTPException(status_code=401, detail="Autenticación requerida")
        principal = _decode_principal(token)

    # Confirma estado y sede contra la base para no confiar solo en claims antiguos.
    async with AsyncSessionLocal() as session:
        user = await UsuariosRepository(session).get_by_id(principal.usuario_id)
        if not user or not user.activo:
            raise HTTPException(status_code=401, detail="Usuario inexistente o inactivo")
        if user.debe_cambiar_password and request.url.path != "/api/v1/auth/cambiar-password-obligatorio":
            raise HTTPException(status_code=403, detail="Debe cambiar la contraseña temporal antes de continuar")
        if user.sede_id != principal.sede_id:
            raise HTTPException(status_code=401, detail="La sede del token ya no es válida")
        requested_sede = request.path_params.get("sede_id") or request.query_params.get("sede_id")
        if requested_sede:
            try:
                is_other_sede = int(requested_sede) != principal.sede_id
            except (TypeError, ValueError) as exc:
                raise HTTPException(status_code=400, detail="Identificador de sede inválido") from exc
            if is_other_sede and not principal.puede_acceder_modulo("Sedes", "Seguridad"):
                raise HTTPException(status_code=403, detail="No puede operar sobre otra sede")
    return principal


def require_permissions(*required: str):
    async def dependency(request: Request) -> AuthPrincipal:
        principal = await get_current_principal(request)
        missing = [permission for permission in required if not principal.tiene_permiso(permission)]
        if missing:
            raise HTTPException(status_code=403, detail=f"Permisos requeridos: {', '.join(missing)}")
        return principal

    return dependency


def require_module_access(*aliases: str):
    async def dependency(request: Request) -> AuthPrincipal:
        principal = await get_current_principal(request)
        if not principal.puede_acceder_modulo(*aliases):
            raise HTTPException(status_code=403, detail="Permiso insuficiente para este módulo")
        return principal

    return dependency

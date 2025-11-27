# app/kernel/domain/seguridad/errors.py


class SeguridadError(Exception):
    """Base para errores del subdominio Seguridad."""
    pass


class UsuarioNoEncontrado(SeguridadError):
    status_code = 404
    code = "USUARIO_NOT_FOUND"


class CredencialesInvalidas(SeguridadError):
    status_code = 401
    code = "CREDENCIALES_INVALID"


class UsuarioInactivo(SeguridadError):
    status_code = 403
    code = "USUARIO_INACTIVE"


class PermisoDenegado(SeguridadError):
    status_code = 403
    code = "PERMISO_DENIED"


class RolNoEncontrado(SeguridadError):
    status_code = 404
    code = "ROL_NOT_FOUND"

class RolNombreDuplicado(SeguridadError):
    status_code = 409
    code = "ROL_DUPLICATED"


class RolEnUso(SeguridadError):
    status_code = 409
    code = "ROL_IN_USE"


class TokenInvalido(SeguridadError):
    status_code = 401
    code = "TOKEN_INVALID"


class TokenExpirado(SeguridadError):
    status_code = 401
    code = "TOKEN_EXPIRED"


class TokenRevocado(SeguridadError):
    status_code = 401
    code = "TOKEN_INVALID" 

class SedeNoEncontrada(SeguridadError):
    status_code = 404
    code = "SEDE_NOT_FOUND"

class SedeCodigoDuplicado(SeguridadError):
    """Se lanza cuando el código de sede ya existe (unicidad global)."""
    status_code = 409
    code = "CODIDIGO_SEDE_DUPLICATED"

# ===== Usuario-Rol =====

class UsuarioRolYaAsignado(SeguridadError):
    """Se lanza cuando se intenta asignar un rol que el usuario ya tiene."""
    status_code = 409
    code = "USUARIO_ROL_ALREADY_ASSIGNED"

class UsuarioRolNoEncontrado(SeguridadError):
    """Se lanza cuando no existe la asignación usuario-rol especificada."""
    status_code = 404
    code = "USUARIO_ROL_NOT_FOUND"

# ===== Rol-Permiso =====

class RolPermisoYaAsignado(SeguridadError):
    """Se lanza cuando se intenta asignar un permiso que el rol ya tiene."""
    status_code = 409
    code = "ROL_PERMISO_ALREADY_ASSIGNED"

class RolPermisoNoEncontrado(SeguridadError):
    """Se lanza cuando no existe la asignación rol-permiso especificada."""
    status_code = 404
    code = "ROL_PERMISO_NOT_FOUND"

# ===== Permisos =====

class PermisoNoEncontrado(SeguridadError):
    status_code = 404
    code = "PERMISO_NOT_FOUND"

class PermisoYaExiste(SeguridadError):
    """Se lanza cuando se intenta crear un permiso que ya existe (recurso + acción)."""
    status_code = 409
    code = "PERMISO_ALREADY_EXISTS"

class UsuarioYaExiste(SeguridadError):
    """Se lanza cuando se intenta crear un usuario con username ya existente."""
    status_code = 409
    code = "USUARIO_ALREADY_EXISTS"

class UsuarioEmailDuplicado(SeguridadError):
    """Se lanza cuando el email ya está registrado."""
    status_code = 409
    code = "USUARIO_EMAIL_DUPLICATED"

class RolNoPermitidoParaCreacion(SeguridadError):
    """Se lanza cuando se intenta crear un usuario con un rol no permitido manualmente."""
    status_code = 403
    code = "ROL_NOT_ALLOWED_FOR_MANUAL_CREATION"

class UsuarioNoEncontrado(SeguridadError):
    status_code = 404
    code = "USUARIO_NOT_FOUND"

class UsuarioYaExiste(SeguridadError):
    """Se lanza cuando se intenta crear un usuario con username ya existente."""
    status_code = 409
    code = "USUARIO_ALREADY_EXISTS"

class UsuarioEmailDuplicado(SeguridadError):
    """Se lanza cuando el email ya está registrado."""
    status_code = 409
    code = "USUARIO_EMAIL_DUPLICATED"
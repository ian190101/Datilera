# app/kernel/domain/seguridad/errors.py

class SeguridadError(Exception):
    """Base para errores del subdominio Seguridad."""
    pass


class UsuarioNoEncontrado(SeguridadError):
    pass


class CredencialesInvalidas(SeguridadError):
    pass


class UsuarioInactivo(SeguridadError):
    pass


class PermisoDenegado(SeguridadError):
    pass


class RolNoEncontrado(SeguridadError):
    pass


class TokenInvalido(SeguridadError):
    pass


class TokenExpirado(SeguridadError):
    pass


class TokenRevocado(SeguridadError):
    pass

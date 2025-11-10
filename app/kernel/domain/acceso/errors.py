# app/kernel/domain/acceso/errors.py

class AccesoError(Exception):
    """Base para errores del subdominio Acceso."""
    pass


class CodigoNoEncontrado(AccesoError):
    pass


class CodigoInvalido(AccesoError):
    """Formato/valor no válido (no cumple 6 alfanuméricos o checksum si aplicas)."""
    pass


class CodigoExpirado(AccesoError):
    pass


class CodigoRevocado(AccesoError):
    pass


class CodigoAgotado(AccesoError):
    """Se alcanzó el límite de usos permitidos."""
    pass


class VerificacionNoPermitida(AccesoError):
    """p.ej., código no vigente en la fecha/hora de verificación."""
    pass

from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi import HTTPException as FastAPIHTTPException
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from loguru import logger

from app.kernel.domain.common.excepciones import BaseDominioError
from app.kernel.domain.seguridad.errors import (
    CredencialesInvalidas, UsuarioInactivo, UsuarioNoEncontrado,
    TokenInvalido, TokenExpirado, RolNoEncontrado, PermisoDenegado
)

async def global_exception_handler(request: Request, exc: Exception):
    """
    Manejador global: resume y mapea excepciones de dominio/HTTP/otras en un JSON estándar.
    """
    if isinstance(exc, BaseDominioError):
        status_code = getattr(exc, 'status_code', 400) or 400
        error_code = getattr(exc, 'code', 'DOMAIN_ERROR') or 'DOMAIN_ERROR'
        message = getattr(exc, 'message', str(exc))
    elif isinstance(exc, (FastAPIHTTPException, StarletteHTTPException)):
        status_code = exc.status_code
        error_code = status_code
        message = exc.detail
    else:
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        error_code = "SERVER_ERROR"
        message = "Un error inesperado ha ocurrido. Por favor, intente de nuevo más tarde."
        logger.error(f"Error 500 No Controlado: {exc.__class__.__name__}: {exc}")
    response_content = {
        "status": "error",
        "code": error_code,
        "message": message,
        "details": getattr(exc, 'details', None)
    }
    return JSONResponse(status_code=status_code, content=response_content)


def register_handlers(app):
    # Manejadores específicos: SIEMPRE por clase
    @app.exception_handler(CredencialesInvalidas)
    async def _cred(_: Request, exc: CredencialesInvalidas):
        return JSONResponse(status_code=401, content={"detail": str(exc) or "Credenciales inválidas"})

    @app.exception_handler(UsuarioInactivo)
    async def _inac(_: Request, exc: UsuarioInactivo):
        return JSONResponse(status_code=403, content={"detail": "Usuario inactivo"})

    @app.exception_handler(TokenInvalido)
    async def _tok_invalido(_: Request, exc: TokenInvalido):
        return JSONResponse(status_code=401, content={"detail": "Token inválido o expirado"})

    @app.exception_handler(TokenExpirado)
    async def _tok_expirado(_: Request, exc: TokenExpirado):
        return JSONResponse(status_code=401, content={"detail": "Token inválido o expirado"})

    @app.exception_handler(RolNoEncontrado)
    async def _rol_no_encontrado(_: Request, exc: RolNoEncontrado):
        return JSONResponse(status_code=403, content={"detail": "Permiso denegado"})

    @app.exception_handler(PermisoDenegado)
    async def _permiso_denegado(_: Request, exc: PermisoDenegado):
        return JSONResponse(status_code=403, content={"detail": "Permiso denegado"})

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": exc.errors(), "body": exc.body}
        )

    @app.exception_handler(FastAPIHTTPException)
    async def fastapi_http_exception_handler(request: Request, exc: FastAPIHTTPException):
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

    @app.exception_handler(StarletteHTTPException)
    async def starlette_http_exception_handler(request: Request, exc: StarletteHTTPException):
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

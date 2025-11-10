# app/main.py
from __future__ import annotations
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, status
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager
from loguru import logger
import logging
import uvicorn

from app.config.settings import get_settings
from app.infrastructure.db.session import dispose_engine
from app.middleware.exception_handler import global_exception_handler, register_handlers
from app.kernel.domain.common.excepciones import BaseDominioError
from fastapi import HTTPException as StarletteHTTPException
from pydantic import ValidationError
from starlette.requests import Request

from app.interfaces.api.v1 import seguridad as seguridad_router
from app.interfaces.api.v1 import acceso as acceso_router
from app.config.settings import get_settings

settings = get_settings()
#DATABASE_URL = Settings.database_url 


@asynccontextmanager
async def lifespan(app: FastAPI):
    if not settings.sql_echo:
        logging.getLogger("sqlalchemy.engine").setLevel(settings.log_level)
    logger.add(f"logs/datilera_{settings.environment}_{{time}}.log", rotation="10 MB", level=settings.log_level)
    logger.info(f"Iniciando API de Datilera en ambiente: {settings.environment}")
    yield
    logger.info("Cerrando motor de base de datos...")
    await dispose_engine()

def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version="1.0.0",
        openapi_url="/api/openapi.json",
        lifespan=lifespan,
        debug=settings.debug,
    )

    # Middleware de excepciones global (envolvente)
    async def exception_middleware(request: Request, call_next):
        try:
            return await call_next(request)
        except Exception as exc:
            return await global_exception_handler(request, exc)
    app.add_middleware(BaseHTTPMiddleware, dispatch=exception_middleware)  # envuelve resto [web:648][web:643]

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(o) for o in settings.cors_origins] if settings.cors_origins else ["*"],
        allow_credentials=settings.cors_allow_credentials,
        allow_methods=settings.cors_allow_methods,
        allow_headers=settings.cors_allow_headers,
    )  # [web:648]

    # Trusted hosts (opcional, útil en prod)
    if settings.trusted_hosts:
        app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.trusted_hosts)  # [web:651]

    # Handlers específicos (además del middleware)
    @app.exception_handler(BaseDominioError)
    async def _dom_exc(request: Request, exc: BaseDominioError):
        return await global_exception_handler(request, exc)  # [file:598]
    @app.exception_handler(StarletteHTTPException)
    async def _http_exc(request: Request, exc: StarletteHTTPException):
        return await global_exception_handler(request, exc)  # [file:598]
    @app.exception_handler(ValidationError)
    async def _val_exc(request: Request, exc: ValidationError):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"status": "error", "code": "VALIDATION_ERROR", "message": "Error de validación", "details": exc.errors()},
        )  # [file:598]

    # Routers
    app.include_router(seguridad_router.router, prefix="/api/v1")  # /api/v1/auth/* [file:598]
    app.include_router(acceso_router.router, prefix="/api/v1") 

    # Registrar mapeos de errores de dominio (401/403)
    register_handlers(app)  # [file:598]

    # Health-checks
    @app.get("/health", include_in_schema=False)
    async def health():
        return {"status": "ok"}  # [web:655]
    @app.get("/", include_in_schema=False)
    async def root():
        return RedirectResponse(url="/docs", status_code=status.HTTP_302_FOUND)  # [file:598]

    return app

app = create_app()

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=settings.debug)

# app/main.py
from __future__ import annotations
from dotenv import load_dotenv
load_dotenv()

import os
from fastapi import FastAPI, Request, status, Request
from pathlib import Path
from fastapi.responses import RedirectResponse, JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
from loguru import logger
import logging
import uvicorn
import gzip
import io

from app.config.settings import get_settings
from app.infrastructure.db.session import dispose_engine
from app.middleware.exception_handler import global_exception_handler, register_handlers
from app.kernel.domain.common.excepciones import BaseDominioError
from fastapi import HTTPException as StarletteHTTPException
from pydantic import ValidationError

# Importar routers de API
from app.interfaces.api.v1 import seguridad as seguridad_router
from app.interfaces.api.v1 import acceso as acceso_router
from app.interfaces.api.v1 import inventario as inventario_router
from app.interfaces.api.v1 import academico as academico_router
from app.interfaces.api.v1 import sedes as sede_router
from app.interfaces.api.v1 import roles as rol_router
from app.interfaces.api.v1 import usuario_roles as usuario_rol_router
from app.interfaces.api.v1 import rol_permisos as rol_permiso_router
from app.interfaces.api.v1 import permisos as permiso_router
from app.interfaces.api.v1 import usuarios as usuario_router
from app.interfaces.api.v1 import finanzas as finanza_router
from app.interfaces.api.v1 import inscripcion as inscripcion_router
from app.interfaces.api.v1 import portafolio as portafolio_router
from app.interfaces.api.v1 import conversaciones as conversacion_router
from app.interfaces.api.v1 import mensajes as mensaje_router
from app.interfaces.api.v1 import notificaciones as notificacion_router
from app.interfaces.api.v1 import estadisticas_comunicaciones as estcom_router
from app.interfaces.api.v1 import alumnos as alumno_router
#from app.interfaces.api.v1 import cursos_extra as cursoextra_router
from app.interfaces.api.v1 import auditoria as auditoria_router
from app.interfaces.api.v1 import ia as ia_router
from app.interfaces.api.v1 import calendario as calendario_router
from app.interfaces.api.v1 import multimedia_marca_agua as marca_router
from app.interfaces.api.v1 import exportaciones as exportacion_router
from app.interfaces.api.v1 import ws as ws_router

settings = get_settings()

# ============================================================
# CONFIGURACIÓN DE PATHS
# ============================================================
STATIC_DIR = Path(settings.STATIC_DIR)
TEMPLATES_DIR = Path(settings.TEMPLATES_DIR)
MEDIA_DIR = Path(settings.MEDIA_DIR)
PDF_DIR = Path(settings.PDF_DIR)

# Crear directorios si no existen
STATIC_DIR.mkdir(parents=True, exist_ok=True)
TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)
MEDIA_DIR.mkdir(parents=True, exist_ok=True)
PDF_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================
# CONFIGURAR TEMPLATES JINJA2
# ============================================================
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# Filtros personalizados
def format_currency(value):
    """Formatea números como moneda boliviana"""
    if value is None:
        return "Bs 0.00"
    return f"Bs {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def format_date(value, format="%d/%m/%Y"):
    """Formatea fechas"""
    if value is None:
        return ""
    if isinstance(value, str):
        from datetime import datetime
        value = datetime.fromisoformat(value.replace("Z", "+00:00"))
    return value.strftime(format)

templates.env.filters["currency"] = format_currency
templates.env.filters["date"] = format_date
templates.env.globals["APP_NAME"] = settings.app_name
templates.env.globals["ENV"] = settings.environment


# ============================================================
# LIFECYCLE
# ============================================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestión del ciclo de vida de la aplicación"""
    # Startup
    if not settings.sql_echo:
        logging.getLogger("sqlalchemy.engine").setLevel(settings.log_level)
    logger.add(
        f"logs/datilera_{settings.environment}_{{time}}.log",
        rotation="10 MB",
        level=settings.log_level
    )
    logger.info(f"Iniciando API de Datilera en ambiente: {settings.environment}")
    
    print(f"\n{'='*60}")
    print(f"✅ {settings.app_name} - Servidor iniciado ({settings.environment.upper()})")
    print(f"{'='*60}")
    print(f"📁 Archivos estáticos: {STATIC_DIR}")
    print(f"📄 Templates:          {TEMPLATES_DIR}")
    print(f"🖼️  Media:             {MEDIA_DIR}")
    print(f"📋 PDFs:              {PDF_DIR}")
    print(f"🌐 API Docs:          http://localhost:8000/api/docs")
    print(f"🖥️  Frontend:          http://localhost:8000/")
    print(f"{'='*60}\n")
    
    yield
    
    # Shutdown
    logger.info("Cerrando motor de base de datos...")
    await dispose_engine()
    print(f"\n⛔ {settings.app_name} - Servidor detenido\n")


# ============================================================
# CREAR APLICACIÓN FASTAPI
# ============================================================
def create_app() -> FastAPI:
    """Factory para crear la instancia de FastAPI"""
    
    app = FastAPI(
        title=settings.app_name,
        version="1.0.0",
        openapi_url="/api/openapi.json",
        docs_url="/api/docs" if settings.environment == "dev" else None,
        redoc_url="/api/redoc" if settings.environment == "dev" else None,
        lifespan=lifespan,
        debug=settings.debug,
    )

    # ============================================================
    # MONTAR ARCHIVOS ESTÁTICOS
    # ============================================================
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
    app.mount("/media", StaticFiles(directory=str(MEDIA_DIR)), name="media")
    app.mount("/pdf", StaticFiles(directory=str(PDF_DIR)), name="pdf")

    

    # ============================================================
    # MIDDLEWARES
    # ============================================================
    
    # Middleware de excepciones global (debe ir primero)
    async def exception_middleware(request: Request, call_next):
        try:
            return await call_next(request)
        except Exception as exc:
            return await global_exception_handler(request, exc)
    
    app.add_middleware(BaseHTTPMiddleware, dispatch=exception_middleware)

    # 2. Middleware de Log Seguro (SOLUCIÓN AL ERROR DE FOTO)
    @app.middleware("http")
    async def log_request_middleware(request: Request, call_next):
        content_type = request.headers.get('content-type', '')
        # Si es subida de archivos, NO intentamos leer el body para no corromperlo
        if "multipart/form-data" in content_type:
            logger.info(f"📁 Subida de Archivo: {request.method} {request.url}")
            return await call_next(request)
        
        # Si es normal, procesamos
        return await call_next(request)
    
    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(o) for o in settings.cors_origins] if settings.cors_origins else ["*"],
        allow_credentials=settings.cors_allow_credentials,
        allow_methods=settings.cors_allow_methods,
        allow_headers=settings.cors_allow_headers,
    )

    # Compresión GZip
    app.add_middleware(GZipMiddleware, minimum_size=1000)

    # Trusted hosts (opcional, útil en producción)
    if settings.trusted_hosts:
        app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.trusted_hosts)


    
    # ============================================================
    # EXCEPTION HANDLERS
    # ============================================================
    
    @app.exception_handler(BaseDominioError)
    async def _dom_exc(request: Request, exc: BaseDominioError):
        return await global_exception_handler(request, exc)

    @app.exception_handler(StarletteHTTPException)
    async def _http_exc(request: Request, exc: StarletteHTTPException):
        return await global_exception_handler(request, exc)

    @app.exception_handler(ValidationError)
    async def _val_exc(request: Request, exc: ValidationError):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "status": "error",
                "code": "VALIDATION_ERROR",
                "message": "Error de validación",
                "details": exc.errors()
            },
        )

    @app.exception_handler(404)
    async def custom_404_handler(request: Request, exc):
        """Página 404 personalizada"""
        if request.url.path.startswith("/api/"):
            return JSONResponse(
                status_code=404,
                content={"detail": "Endpoint no encontrado"}
            )
        
        try:
            return templates.TemplateResponse(
                "errors/404.html",
                {"request": request, "page_title": "Página no encontrada"},
                status_code=404
            )
        except:
            return HTMLResponse(
                content="<h1>404 - Página no encontrada</h1>",
                status_code=404
            )

    @app.exception_handler(500)
    async def custom_500_handler(request: Request, exc):
        """Página 500 personalizada"""
        if request.url.path.startswith("/api/"):
            return JSONResponse(
                status_code=500,
                content={"detail": "Error interno del servidor"}
            )
        
        try:
            return templates.TemplateResponse(
                "errors/500.html",
                {"request": request, "page_title": "Error del servidor"},
                status_code=500
            )
        except:
            return HTMLResponse(
                content="<h1>500 - Error interno del servidor</h1>",
                status_code=500
            )

    # ============================================================
    # REGISTRAR ROUTERS DE API
    # ============================================================
    
    app.include_router(seguridad_router.router, prefix="/api/v1")
    app.include_router(acceso_router.router, prefix="/api/v1")
    app.include_router(inventario_router.router, prefix="/api/v1")
    app.include_router(academico_router.router, prefix="/api/v1")
    app.include_router(sede_router.router, prefix="/api/v1")
    app.include_router(rol_router.router, prefix="/api/v1")
    app.include_router(usuario_rol_router.router, prefix="/api/v1")
    app.include_router(rol_permiso_router.router, prefix="/api/v1")
    app.include_router(permiso_router.router, prefix="/api/v1")
    app.include_router(usuario_router.router, prefix="/api/v1")
    app.include_router(finanza_router.router, prefix="/api/v1")
    app.include_router(inscripcion_router.router, prefix="/api/v1")
    app.include_router(portafolio_router.router, prefix="/api/v1")
    app.include_router(conversacion_router.router, prefix="/api/v1")
    app.include_router(mensaje_router.router, prefix="/api/v1")
    app.include_router(notificacion_router.router, prefix="/api/v1")
    app.include_router(estcom_router.router, prefix="/api/v1")
    app.include_router(alumno_router.router, prefix="/api/v1")
    #app.include_router(cursoextra_router.router, prefix="/api/v1")
    app.include_router(auditoria_router.router, prefix="/api/v1")
    app.include_router(ia_router.router, prefix="/api/v1")
    app.include_router(calendario_router.router, prefix="/api/v1")
    app.include_router(marca_router.router, prefix="/api/v1")
    app.include_router(exportacion_router.router, prefix="/api/v1")
    app.include_router(ws_router.router, prefix="/api/v1")

    # ============================================================
    # REGISTRAR ROUTER DE FRONTEND WEB
    # ============================================================
    
    from app.interfaces.web.routes import web_router
    app.include_router(web_router)

    # ============================================================
    # REGISTRAR HANDLERS DE DOMINIO
    # ============================================================
    
    register_handlers(app)

    # ============================================================
    # PARCHE CRÍTICO PARA FOTOS (SOBREESCRIBIR HANDLER)
    # ============================================================
    # Esto evita el error "FormData is not JSON serializable"
    # al impedir que se incluya el cuerpo del archivo en el error.
    @app.exception_handler(RequestValidationError)
    async def safe_validation_exception_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "detail": exc.errors(), 
                "message": "Error de validación en los datos enviados"
                # NO incluimos exc.body aquí porque es un archivo y rompe el JSON
            }
        )


    # ============================================================
    # HEALTH CHECKS
    # ============================================================
    
    @app.get("/health", include_in_schema=False)
    async def health():
        return {
            "status": "ok",
            "service": settings.app_name,
            "environment": settings.environment,
            "version": "1.0.0"
        }

    @app.get("/", include_in_schema=False)
    async def root():
        # Redirigir a docs en desarrollo, a dashboard en producción
        if settings.environment == "dev":
            return RedirectResponse(url="/api/docs", status_code=status.HTTP_302_FOUND)
        else:
            return RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)

    return app


# ============================================================
# CREAR INSTANCIA DE APP
# ============================================================
app = create_app()



# ============================================================
# ENTRY POINT
# ============================================================
if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level="debug" if settings.debug else "info"
    )

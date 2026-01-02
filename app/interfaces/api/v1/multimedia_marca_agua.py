# app/interfaces/api/v1/multimedia.py

from __future__ import annotations
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.session import get_session
from app.infrastructure.db.repositories.portafolio.actividad_media_repo import (
    ActividadMediaRepository
)

# Casos de Uso
from app.kernel.application.portafolio.media.obtener_estado_procesamiento import (
    ObtenerEstadoProcesamientoCU,
    ObtenerEstadoProcesamientoIn,
    ObtenerEstadoProcesamientoOut,
)
from app.kernel.application.portafolio.media.reprocesar_archivo import (
    ReprocesarArchivoCU,
    ReprocesarArchivoIn,
    ReprocesarArchivoOut,
)
from app.kernel.application.portafolio.media.listar_archivos_cola import (
    ListarArchivosColaCU,
    ListarArchivosColaIn,
    ListarArchivosColaOut,
)
from app.kernel.application.portafolio.media.reintentar_errores_masivo import (
    ReintentarErroresMasivoCU,
    ReintentarErroresMasivoIn,
    ReintentarErroresMasivoOut,
)

# Errores de dominio
from app.kernel.domain.portafolio import (
    MediaNoEncontradaError,
    MediaProcesamientoError,
    MediaIntentosExcedidosError,
)

from fastapi import HTTPException


router = APIRouter(prefix="/multimedia", tags=["Multimedia - Marca de Agua"])


# ========================================================================
# DEPENDENCIAS
# ========================================================================

async def get_media_repository(
    db: Annotated[AsyncSession, Depends(get_session)]
) -> ActividadMediaRepository:
    """Factory para el repositorio de multimedia."""
    return ActividadMediaRepository(db)


# ========================================================================
# ENDPOINTS
# ========================================================================

@router.get(
    "/estado/{media_id}",
    response_model=ObtenerEstadoProcesamientoOut,
    status_code=status.HTTP_200_OK,
    summary="Obtener estado de procesamiento",
    description="""
    Obtiene el estado de procesamiento de marca de agua de un archivo multimedia.
    
    **Retorna:**
    - Estado actual (pendiente, procesando, completado, error, no_aplica)
    - Número de intentos de procesamiento
    - Mensaje de error si falló
    - ID de la cola de procesamiento (Celery/RQ)
    - Fecha de procesamiento completado
    - URLs (original y con marca de agua)
    
    **Útil para:**
    - Verificar si un archivo ya está listo para descargar
    - Diagnosticar errores de procesamiento
    - Monitorear progreso de archivos en cola
    """,
)
async def obtener_estado_procesamiento(
    media_id: int,
    repo: Annotated[ActividadMediaRepository, Depends(get_media_repository)],
):
    """Endpoint para consultar estado de procesamiento de marca de agua."""
    try:
        caso_uso = ObtenerEstadoProcesamientoCU(media_repo=repo)
        resultado = await caso_uso(ObtenerEstadoProcesamientoIn(media_id=media_id))
        return resultado
    
    except MediaNoEncontradaError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message
        )


@router.post(
    "/reprocesar/{media_id}",
    response_model=ReprocesarArchivoOut,
    status_code=status.HTTP_200_OK,
    summary="Reprocesar archivo",
    description="""
    Fuerza el reprocesamiento de un archivo con marca de agua.
    
    **Casos de uso:**
    - El archivo falló por error temporal (red, disco, etc.)
    - Se cambió la configuración de marca de agua
    - El archivo nunca se procesó desde su subida
    
    **No permite reprocesar si:**
    - Ya está completado correctamente
    - Excedió el máximo de intentos (3)
    - Está marcado como "no aplica"
    
    **Retorna:**
    - Archivo actualizado
    - Nuevo ID de cola asignado
    - Número de intentos actual
    """,
)
async def reprocesar_archivo(
    media_id: int,
    repo: Annotated[ActividadMediaRepository, Depends(get_media_repository)],
):
    """Endpoint para forzar reprocesamiento de marca de agua."""
    try:
        caso_uso = ReprocesarArchivoCU(media_repo=repo)
        resultado = await caso_uso(ReprocesarArchivoIn(media_id=media_id))
        return resultado
    
    except MediaNoEncontradaError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message
        )
    
    except MediaProcesamientoError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{e.message}: {e.razon}"
        )
    
    except MediaIntentosExcedidosError as e:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"{e.message}: {e.intentos}/{e.max_intentos} intentos"
        )


@router.get(
    "/cola/pendientes",
    response_model=ListarArchivosColaOut,
    status_code=status.HTTP_200_OK,
    summary="Listar archivos pendientes",
    description="""
    Lista archivos pendientes de procesamiento o en procesamiento.
    
    **Útil para:**
    - Monitorear la cola de procesamiento
    - Detectar archivos estancados
    - Dashboard de administración
    
    **Retorna:**
    - Lista de archivos con estado PENDIENTE o PROCESANDO
    - Total de archivos encontrados
    """,
)
async def listar_archivos_pendientes(
    limite: int = Query(
        default=50,
        ge=1,
        le=200,
        description="Límite de resultados"
    ),
    *,
    repo: Annotated[ActividadMediaRepository, Depends(get_media_repository)],
):
    """Endpoint para listar archivos pendientes de procesamiento."""
    caso_uso = ListarArchivosColaCU(media_repo=repo)
    resultado = await caso_uso(
        ListarArchivosColaIn(tipo="pendientes", limite=limite)
    )
    return resultado


@router.get(
    "/cola/errores",
    response_model=ListarArchivosColaOut,
    status_code=status.HTTP_200_OK,
    summary="Listar archivos con error",
    description="""
    Lista archivos que fallaron al procesarse.
    
    **Incluye:**
    - Mensaje de error detallado
    - Número de intentos realizados
    - Timestamp del último intento
    - ID de cola del último intento
    
    **Útil para:**
    - Diagnosticar problemas de procesamiento
    - Identificar archivos problemáticos
    - Decidir si reintentar o descartar
    """,
)
async def listar_archivos_con_error(
    limite: int = Query(
        default=50,
        ge=1,
        le=200,
        description="Límite de resultados"
    ),
    *,
    repo: Annotated[ActividadMediaRepository, Depends(get_media_repository)],
):
    """Endpoint para listar archivos con error de procesamiento."""
    caso_uso = ListarArchivosColaCU(media_repo=repo)
    resultado = await caso_uso(
        ListarArchivosColaIn(tipo="errores", limite=limite)
    )
    return resultado


@router.post(
    "/cola/reintentar-errores",
    response_model=ReintentarErroresMasivoOut,
    status_code=status.HTTP_200_OK,
    summary="Reintentar archivos con error",
    description="""
    Reintenta procesar todos los archivos con error en lote.
    
    **Solo reintenta archivos que:**
    - Tienen estado ERROR
    - No han excedido el máximo de intentos configurado
    
    **Parámetros:**
    - max_intentos: Límite de intentos antes de descartar (default: 3)
    
    **Útil para:**
    - Recuperación masiva después de un problema del sistema
    - Reintentar después de actualizar configuración
    - Limpieza de cola de errores
    
    **Retorna:**
    - Total de archivos reenviados
    - IDs de los archivos reenviados
    - Mensaje de confirmación
    """,
)
async def reintentar_archivos_con_error(
    max_intentos: int = Query(
        default=3,
        ge=1,
        le=10,
        description="Máximo de intentos permitidos"
    ),
    *,
    repo: Annotated[ActividadMediaRepository, Depends(get_media_repository)],
):
    """Endpoint para reintentar procesamiento masivo de archivos con error."""
    caso_uso = ReintentarErroresMasivoCU(media_repo=repo)
    resultado = await caso_uso(
        ReintentarErroresMasivoIn(max_intentos=max_intentos)
    )
    return resultado


# ========================================================================
# ESTADÍSTICAS (OPCIONAL - BONUS)
# ========================================================================

@router.get(
    "/estadisticas",
    status_code=status.HTTP_200_OK,
    summary="Estadísticas de procesamiento",
    description="""
    Obtiene estadísticas generales de procesamiento de marca de agua.
    
    **Retorna:**
    - Conteo por cada estado (pendiente, procesando, completado, error)
    - Útil para dashboard de monitoreo
    """,
)
async def obtener_estadisticas_procesamiento(
    repo: Annotated[ActividadMediaRepository, Depends(get_media_repository)],
):
    """Endpoint para estadísticas de procesamiento."""
    # TODO: Implementar caso de uso si necesitas este endpoint
    # Por ahora puedes retornar un placeholder
    return {
        "mensaje": "Endpoint de estadísticas - Por implementar",
        "nota": "Requiere caso de uso ObtenerEstadisticasProcesamientoCU"
    }

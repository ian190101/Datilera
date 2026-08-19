# app/interfaces/api/v1/exportacion.py

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query, status, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.session import get_session
from app.middleware.api_auth import AuthPrincipal, get_current_principal

# Repositorios
from app.infrastructure.db.repositories.exportacion.exportacion_repo import (
    ExportacionRepository,
    PlantillaExportacionRepository,
)

# Casos de uso
from app.kernel.application.exportacion.exportar_reporte import (
    ExportarReporteCU,
    ExportarReporteIn,
)
from app.kernel.application.exportacion.exportar_columnas_personalizadas import (
    ExportarColumnasPersonalizadasCU,
    ExportarColumnasPersonalizadasIn,
)
from app.kernel.application.exportacion.obtener_estado_exportacion import (
    ObtenerEstadoExportacionCU,
    ObtenerEstadoExportacionIn,
)
from app.kernel.application.exportacion.descargar_exportacion import (
    DescargarExportacionCU,
    DescargarExportacionIn,
)
from app.kernel.application.exportacion.listar_plantillas import (
    ListarPlantillasCU,
    ListarPlantillasIn,
)
from app.kernel.application.exportacion.crear_plantilla import (
    CrearPlantillaCU,
    CrearPlantillaIn,
)
from app.kernel.application.exportacion.exportar_con_plantilla import (
    ExportarConPlantillaCU,
    ExportarConPlantillaIn,
)
from app.kernel.application.exportacion.listar_historial_exportaciones import (
    ListarHistorialExportacionesCU,
    ListarHistorialExportacionesIn,
)
from app.kernel.application.exportacion.eliminar_exportacion import (
    EliminarExportacionCU,
    EliminarExportacionIn,
)

# Enums
from app.kernel.domain.exportacion import TipoReporte

# Errores de dominio
from app.kernel.domain.exportacion import (
    ExportacionNoEncontradaError,
    ExportacionNoCompletadaError,
    ExportacionExpiradaError,
    ArchivoNoDisponibleError,
    PlantillaNoEncontradaError,
    PlantillaNoAccesibleError,
    PlantillaDuplicadaError,
)


router = APIRouter(prefix="/exportacion", tags=["Exportación"])
SessionDep = Annotated[AsyncSession, Depends(get_session)]


# ===========================================================================
# HELPERS DE INYECCIÓN DE DEPENDENCIAS
# ===========================================================================

def exportacion_repo(db: AsyncSession) -> ExportacionRepository:
    """Helper para crear repositorio de exportaciones."""
    return ExportacionRepository(db)


def plantilla_repo(db: AsyncSession) -> PlantillaExportacionRepository:
    """Helper para crear repositorio de plantillas."""
    return PlantillaExportacionRepository(db)


# TODO: Reemplazar con autenticación real desde JWT
def get_current_user_id(principal: AuthPrincipal = Depends(get_current_principal)) -> int:
    return principal.usuario_id


def get_current_user_sede_id(principal: AuthPrincipal = Depends(get_current_principal)) -> int:
    return principal.sede_id


# ===========================================================================
# ENDPOINTS PRINCIPALES DE EXPORTACIÓN
# ===========================================================================

@router.post("/reporte", status_code=status.HTTP_202_ACCEPTED)
async def exportar_reporte(
    db: SessionDep,
    payload: ExportarReporteIn,
    usuario_id: int = Depends(get_current_user_id),
    sede_id: int = Depends(get_current_user_sede_id),
):
    """
    Exportar cualquier tipo de reporte del sistema.
    
    Soporta 20+ tipos de reportes: académico, financiero, inventarios, etc.
    La exportación es asíncrona (PENDIENTE -> PROCESANDO -> COMPLETADO).
    El archivo expira en 3 días.
    """
    try:
        uc = ExportarReporteCU(
            exportacion_repo=exportacion_repo(db),
            usuario_id=usuario_id,
            sede_id=sede_id,
        )
        return await uc(payload)
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/columnas-personalizadas", status_code=status.HTTP_202_ACCEPTED)
async def exportar_columnas_personalizadas(
    db: SessionDep,
    payload: ExportarColumnasPersonalizadasIn,
    usuario_id: int = Depends(get_current_user_id),
    sede_id: int = Depends(get_current_user_sede_id),
):
    """
    Exportar con columnas seleccionadas por el usuario.
    
    Permite seleccionar exactamente qué columnas exportar.
    Opcionalmente guarda la configuración como plantilla reutilizable.
    """
    try:
        uc = ExportarColumnasPersonalizadasCU(
            exportacion_repo=exportacion_repo(db),
            plantilla_repo=plantilla_repo(db),
            usuario_id=usuario_id,
            sede_id=sede_id,
        )
        return await uc(payload)
    
    except PlantillaDuplicadaError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/{exportacion_id}")
async def obtener_estado_exportacion(
    exportacion_id: int,
    db: SessionDep,
):
    """
    Consultar el estado de una exportación en proceso.
    
    Estados: pendiente, procesando, completado, error.
    """
    try:
        uc = ObtenerEstadoExportacionCU(
            exportacion_repo=exportacion_repo(db),
        )
        return await uc(ObtenerEstadoExportacionIn(exportacion_id=exportacion_id))
    
    except ExportacionNoEncontradaError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.get("/{exportacion_id}/descargar")
async def descargar_exportacion(
    exportacion_id: int,
    db: SessionDep,
):
    """
    Descargar archivo exportado.
    
    Requisitos:
    - Estado COMPLETADO
    - No expirado
    
    Incrementa el contador de descargas.
    """
    try:
        uc = DescargarExportacionCU(
            exportacion_repo=exportacion_repo(db),
        )
        resultado = await uc(DescargarExportacionIn(exportacion_id=exportacion_id))
        
        return FileResponse(
            path=resultado.ruta_archivo,
            filename=resultado.nombre_archivo,
            media_type=resultado.tipo_contenido,
        )
    
    except ExportacionNoEncontradaError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except (ExportacionNoCompletadaError, ExportacionExpiradaError, ArchivoNoDisponibleError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


# ===========================================================================
# ENDPOINTS DE PLANTILLAS
# ===========================================================================

@router.get("/plantillas")
async def listar_plantillas(
    db: SessionDep,
    tipo_reporte: TipoReporte | None = Query(None, description="Filtrar por tipo"),
    solo_publicas: bool = Query(True, description="Solo plantillas públicas"),
    usuario_id: int = Depends(get_current_user_id),
):
    """
    Listar plantillas de exportación disponibles.
    
    Incluye plantillas públicas del sistema y privadas del usuario actual.
    """
    uc = ListarPlantillasCU(
        plantilla_repo=plantilla_repo(db),
        usuario_id=usuario_id if not solo_publicas else None,
    )
    return await uc(ListarPlantillasIn(
        tipo_reporte=tipo_reporte,
        solo_publicas=solo_publicas,
    ))


@router.post("/plantillas", status_code=status.HTTP_201_CREATED)
async def crear_plantilla(
    db: SessionDep,
    payload: CrearPlantillaIn,
    usuario_id: int = Depends(get_current_user_id),
):
    """
    Crear plantilla reutilizable de exportación.
    
    Útil para exportaciones recurrentes.
    Puede ser pública (compartida) o privada.
    """
    try:
        uc = CrearPlantillaCU(
            plantilla_repo=plantilla_repo(db),
            usuario_id=usuario_id,
        )
        return await uc(payload)
    
    except PlantillaDuplicadaError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )


@router.post("/plantillas/{plantilla_id}/usar", status_code=status.HTTP_202_ACCEPTED)
async def exportar_con_plantilla(
    plantilla_id: int,
    db: SessionDep,
    payload: ExportarConPlantillaIn,
    usuario_id: int = Depends(get_current_user_id),
    sede_id: int = Depends(get_current_user_sede_id),
):
    """
    Exportar usando una plantilla predefinida.
    
    Usa la configuración guardada (columnas, filtros, formato).
    Permite sobrescribir filtros específicos si es necesario.
    """
    try:
        payload.plantilla_id = plantilla_id
        
        uc = ExportarConPlantillaCU(
            exportacion_repo=exportacion_repo(db),
            plantilla_repo=plantilla_repo(db),
            usuario_id=usuario_id,
            sede_id=sede_id,
        )
        return await uc(payload)
    
    except PlantillaNoEncontradaError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except PlantillaNoAccesibleError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )


# ===========================================================================
# ENDPOINTS DE HISTORIAL Y GESTIÓN
# ===========================================================================

@router.get("/historial")
async def listar_historial_exportaciones(
    db: SessionDep,
    limite: int = Query(20, ge=1, le=100),
    usuario_id: int = Depends(get_current_user_id),
):
    """
    Listar historial de exportaciones del usuario actual.
    
    Útil para redescargar exportaciones anteriores (si no expiraron).
    """
    uc = ListarHistorialExportacionesCU(
        exportacion_repo=exportacion_repo(db),
        usuario_id=usuario_id,
    )
    return await uc(ListarHistorialExportacionesIn(limite=limite))


@router.delete("/{exportacion_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_exportacion(
    exportacion_id: int,
    db: SessionDep,
):
    """
    Eliminar manualmente una exportación antes de su expiración.
    
    Útil para liberar espacio o eliminar datos sensibles.
    """
    try:
        uc = EliminarExportacionCU(
            exportacion_repo=exportacion_repo(db),
        )
        await uc(EliminarExportacionIn(exportacion_id=exportacion_id))
        return None
    
    except ExportacionNoEncontradaError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )

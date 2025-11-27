# app/interfaces/routers/auditoria.py

"""
Router: Auditoría

Endpoints para:
- Auditoría de acciones (CRUD, login, etc.)
- Tracking de sesiones activas
- Historial de cambios campo por campo
- Control de exportaciones
- Auditoría de consultas a IA
"""
from __future__ import annotations
from typing import List, Dict, Any, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

# Database
from app.infrastructure.db.session import get_session

# Repositorios
from app.infrastructure.db.repositories.auditoria import (
    AuditoriaAccionesRepository,
    AuditoriaSesionesRepository,
    AuditoriaCambiosRepository,
    AuditoriaExportacionesRepository,
    AuditoriaPromptsIARepository,
)

# Casos de Uso
from app.kernel.application.auditoria import (
    # Acciones
    RegistrarAccionCU,
    ListarAccionesCU,
    ObtenerAccionCU,
    BuscarAccionesCU,
    ObtenerEstadisticasCU,
    LimpiarAccionesAntiguasCU,
    # Sesiones
    RegistrarInicioSesionCU,
    ActualizarHeartbeatCU,
    CerrarSesionCU,
    ListarSesionesActivasCU,
    ForzarCierreSesionesCU,
    CerrarSesionesInactivasCU,
    # Cambios
    RegistrarCambioCU,
    RegistrarCambiosMultiplesCU,
    ListarCambiosCU,
    # Exportaciones
    RegistrarExportacionCU,
    MarcarExportacionDescargadaCU,
    ListarExportacionesCU,
    DetectarExportacionesSospechosasCU,
    ObtenerEstadisticasExportacionesCU,
    # Prompts IA
    RegistrarPromptIACU,
    ListarPromptsIACU,
    CalcularConsumoIACU,
    DetectarPromptsSensiblesCU,
    ObtenerEstadisticasIACU,
)

# DTOs
from app.kernel.application.auditoria import (
    # Acciones
    RegistrarAccionDTO,
    ListarAccionesPorUsuarioDTO,
    ListarAccionesPorSedeDTO,
    ListarAccionesPorEntidadDTO,
    ListarAccionesPorNivelDTO,
    ListarErroresDTO,
    BuscarPorDescripcionDTO,
    BuscarPorEndpointDTO,
    BuscarPorIPDTO,
    ObtenerEstadisticasDTO,
    ObtenerActividadPorHoraDTO,
    ObtenerUsuariosMasActivosDTO,
    ObtenerErroresPorEndpointDTO,
    LimpiarAccionesAntiguasDTO,
    # Sesiones
    RegistrarInicioSesionDTO,
    ActualizarHeartbeatDTO,
    CerrarSesionDTO,
    ListarSesionesActivasDTO,
    ForzarCierreSesionesDTO,
    CerrarSesionesInactivasDTO,
    # Cambios
    RegistrarCambioDTO,
    RegistrarCambiosMultiplesDTO,
    ListarCambiosPorAccionDTO,
    ObtenerCambioPorCampoDTO,
    # Exportaciones
    RegistrarExportacionDTO,
    MarcarExportacionDescargadaDTO,
    ListarExportacionesPorUsuarioDTO,
    ListarExportacionesPorSedeDTO,
    ListarExportacionesPorTipoDTO,
    ListarExportacionesFallidasDTO,
    DetectarExportacionesSospechosasDTO,
    ObtenerEstadisticasExportacionesDTO,
    ObtenerTotalRegistrosExportadosDTO,
    # Prompts IA
    RegistrarPromptIADTO,
    ListarPromptsPorUsuarioDTO,
    ListarPromptsPorSedeDTO,
    ListarPromptsConDatosSensiblesDTO,
    ListarPromptsFallidosDTO,
    CalcularTokensConsumidosDTO,
    CalcularCostoTotalDTO,
    DetectarPromptsSensiblesDTO,
    ObtenerEstadisticasIADTO,
    ObtenerDuracionPromedioDTO,
    ObtenerUsuariosMasActivosIADTO,
)

# Errores de dominio
from app.kernel.domain.auditoria import (
    AuditoriaError,
    AccionAuditoriaNoEncontrada,
    SesionAuditoriaNoEncontrada,
    ExportacionAuditoriaNoEncontrada,
    PromptIAAuditoriaNoEncontrado,
)

# Dependencias (ajusta según tu sistema de autenticación)
# from app.interfaces.dependencies.auth import get_current_user, require_permission


# ==============================================================================
# ROUTER
# ==============================================================================

router = APIRouter(prefix="/api/v1/auditoria", tags=["Auditoría"])


# ==============================================================================
# DEPENDENCIAS DE REPOSITORIOS
# ==============================================================================

def get_auditoria_acciones_repo(db: AsyncSession = Depends(get_session)) -> AuditoriaAccionesRepository:
    """Inyección de dependencia: Repositorio de acciones."""
    return AuditoriaAccionesRepository(db)


def get_auditoria_sesiones_repo(db: AsyncSession = Depends(get_session)) -> AuditoriaSesionesRepository:
    """Inyección de dependencia: Repositorio de sesiones."""
    return AuditoriaSesionesRepository(db)


def get_auditoria_cambios_repo(db: AsyncSession = Depends(get_session)) -> AuditoriaCambiosRepository:
    """Inyección de dependencia: Repositorio de cambios."""
    return AuditoriaCambiosRepository(db)


def get_auditoria_exportaciones_repo(db: AsyncSession = Depends(get_session)) -> AuditoriaExportacionesRepository:
    """Inyección de dependencia: Repositorio de exportaciones."""
    return AuditoriaExportacionesRepository(db)


def get_auditoria_prompts_ia_repo(db: AsyncSession = Depends(get_session)) -> AuditoriaPromptsIARepository:
    """Inyección de dependencia: Repositorio de prompts IA."""
    return AuditoriaPromptsIARepository(db)


# ==============================================================================
# ENDPOINTS: AUDITORÍA DE ACCIONES
# ==============================================================================

@router.post(
    "/acciones",
    response_model=Dict[str, Any],
    status_code=status.HTTP_201_CREATED,
    summary="Registrar acción de auditoría",
    description="Registra un evento de auditoría en el sistema."
)
async def registrar_accion(
    dto: RegistrarAccionDTO,
    repo: AuditoriaAccionesRepository = Depends(get_auditoria_acciones_repo)
):
    """Registra una acción de auditoría."""
    try:
        cu = RegistrarAccionCU(repo)
        resultado = await cu.ejecutar(dto)
        return {
            "success": True,
            "message": "Acción de auditoría registrada exitosamente",
            "data": resultado.model_dump()
        }
    except AuditoriaError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.mensaje)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get(
    "/acciones/{auditoria_id}",
    response_model=Dict[str, Any],
    summary="Obtener acción de auditoría",
    description="Obtiene una acción de auditoría por su ID."
)
async def obtener_accion(
    auditoria_id: int,
    repo: AuditoriaAccionesRepository = Depends(get_auditoria_acciones_repo)
):
    """Obtiene una acción de auditoría por ID."""
    try:
        cu = ObtenerAccionCU(repo)
        resultado = await cu.ejecutar(auditoria_id)
        return {
            "success": True,
            "data": resultado.model_dump()
        }
    except AccionAuditoriaNoEncontrada as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.mensaje)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get(
    "/acciones/usuario/{usuario_id}",
    response_model=Dict[str, Any],
    summary="Listar acciones por usuario",
    description="Lista eventos de auditoría de un usuario específico."
)
async def listar_acciones_por_usuario(
    usuario_id: int,
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    repo: AuditoriaAccionesRepository = Depends(get_auditoria_acciones_repo)
):
    """Lista acciones de un usuario."""
    try:
        dto = ListarAccionesPorUsuarioDTO(usuario_id=usuario_id, limit=limit, offset=offset)
        cu = ListarAccionesCU(repo)
        resultados = await cu.por_usuario(dto)
        return {
            "success": True,
            "data": [r.model_dump() for r in resultados],
            "total": len(resultados)
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get(
    "/acciones/sede/{sede_id}",
    response_model=Dict[str, Any],
    summary="Listar acciones por sede",
    description="Lista eventos de auditoría de una sede específica."
)
async def listar_acciones_por_sede(
    sede_id: int,
    desde: Optional[datetime] = Query(None),
    hasta: Optional[datetime] = Query(None),
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    repo: AuditoriaAccionesRepository = Depends(get_auditoria_acciones_repo)
):
    """Lista acciones de una sede."""
    try:
        dto = ListarAccionesPorSedeDTO(
            sede_id=sede_id,
            desde=desde,
            hasta=hasta,
            limit=limit,
            offset=offset
        )
        cu = ListarAccionesCU(repo)
        resultados = await cu.por_sede(dto)
        return {
            "success": True,
            "data": [r.model_dump() for r in resultados],
            "total": len(resultados)
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get(
    "/acciones/entidad/{entidad}",
    response_model=Dict[str, Any],
    summary="Listar acciones por entidad",
    description="Lista eventos de auditoría de una entidad específica (pagos, alumnos, etc.)."
)
async def listar_acciones_por_entidad(
    entidad: str,
    entidad_id: Optional[str] = Query(None),
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    repo: AuditoriaAccionesRepository = Depends(get_auditoria_acciones_repo)
):
    """Lista acciones de una entidad."""
    try:
        dto = ListarAccionesPorEntidadDTO(
            entidad=entidad,
            entidad_id=entidad_id,
            limit=limit,
            offset=offset
        )
        cu = ListarAccionesCU(repo)
        resultados = await cu.por_entidad(dto)
        return {
            "success": True,
            "data": [r.model_dump() for r in resultados],
            "total": len(resultados)
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get(
    "/acciones/errores",
    response_model=Dict[str, Any],
    summary="Listar errores",
    description="Lista solo eventos de auditoría con errores."
)
async def listar_errores(
    sede_id: Optional[int] = Query(None),
    desde: Optional[datetime] = Query(None),
    hasta: Optional[datetime] = Query(None),
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    repo: AuditoriaAccionesRepository = Depends(get_auditoria_acciones_repo)
):
    """Lista solo eventos con errores."""
    try:
        dto = ListarErroresDTO(
            sede_id=sede_id,
            desde=desde,
            hasta=hasta,
            limit=limit,
            offset=offset
        )
        cu = ListarAccionesCU(repo)
        resultados = await cu.errores(dto)
        return {
            "success": True,
            "data": [r.model_dump() for r in resultados],
            "total": len(resultados)
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get(
    "/acciones/buscar/descripcion",
    response_model=Dict[str, Any],
    summary="Buscar por descripción",
    description="Busca eventos de auditoría por texto en descripción."
)
async def buscar_por_descripcion(
    termino: str = Query(..., min_length=1),
    sede_id: Optional[int] = Query(None),
    limit: int = Query(default=50, ge=1, le=100),
    repo: AuditoriaAccionesRepository = Depends(get_auditoria_acciones_repo)
):
    """Busca acciones por descripción."""
    try:
        dto = BuscarPorDescripcionDTO(termino=termino, sede_id=sede_id, limit=limit)
        cu = BuscarAccionesCU(repo)
        resultados = await cu.por_descripcion(dto)
        return {
            "success": True,
            "data": [r.model_dump() for r in resultados],
            "total": len(resultados)
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get(
    "/acciones/estadisticas/por-accion",
    response_model=Dict[str, Any],
    summary="Estadísticas por acción",
    description="Obtiene conteo de eventos agrupados por tipo de acción."
)
async def estadisticas_por_accion(
    sede_id: Optional[int] = Query(None),
    desde: Optional[datetime] = Query(None),
    hasta: Optional[datetime] = Query(None),
    repo: AuditoriaAccionesRepository = Depends(get_auditoria_acciones_repo)
):
    """Estadísticas por acción."""
    try:
        dto = ObtenerEstadisticasDTO(sede_id=sede_id, desde=desde, hasta=hasta)
        cu = ObtenerEstadisticasCU(repo)
        resultado = await cu.por_accion(dto)
        return {
            "success": True,
            "data": resultado
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# ==============================================================================
# ENDPOINTS: AUDITORÍA DE SESIONES
# ==============================================================================

@router.post(
    "/sesiones/inicio",
    response_model=Dict[str, Any],
    status_code=status.HTTP_201_CREATED,
    summary="Registrar inicio de sesión",
    description="Registra cuando un usuario inicia sesión."
)
async def registrar_inicio_sesion(
    dto: RegistrarInicioSesionDTO,
    repo: AuditoriaSesionesRepository = Depends(get_auditoria_sesiones_repo)
):
    """Registra inicio de sesión."""
    try:
        cu = RegistrarInicioSesionCU(repo)
        resultado = await cu.ejecutar(dto)
        return {
            "success": True,
            "message": "Inicio de sesión registrado",
            "data": resultado.model_dump()
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post(
    "/sesiones/heartbeat",
    response_model=Dict[str, Any],
    summary="Actualizar heartbeat",
    description="Actualiza timestamp de última actividad de una sesión."
)
async def actualizar_heartbeat(
    dto: ActualizarHeartbeatDTO,
    repo: AuditoriaSesionesRepository = Depends(get_auditoria_sesiones_repo)
):
    """Actualiza heartbeat de sesión."""
    try:
        cu = ActualizarHeartbeatCU(repo)
        await cu.ejecutar(dto)
        return {
            "success": True,
            "message": "Heartbeat actualizado"
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post(
    "/sesiones/cerrar",
    response_model=Dict[str, Any],
    summary="Cerrar sesión",
    description="Registra el cierre de una sesión de usuario."
)
async def cerrar_sesion(
    dto: CerrarSesionDTO,
    repo: AuditoriaSesionesRepository = Depends(get_auditoria_sesiones_repo)
):
    """Cierra una sesión."""
    try:
        cu = CerrarSesionCU(repo)
        await cu.ejecutar(dto)
        return {
            "success": True,
            "message": "Sesión cerrada"
        }
    except SesionAuditoriaNoEncontrada as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.mensaje)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get(
    "/sesiones/activas",
    response_model=Dict[str, Any],
    summary="Listar sesiones activas",
    description="Lista sesiones activas en el sistema."
)
async def listar_sesiones_activas(
    sede_id: Optional[int] = Query(None),
    usuario_id: Optional[int] = Query(None),
    repo: AuditoriaSesionesRepository = Depends(get_auditoria_sesiones_repo)
):
    """Lista sesiones activas."""
    try:
        dto = ListarSesionesActivasDTO(sede_id=sede_id, usuario_id=usuario_id)
        cu = ListarSesionesActivasCU(repo)
        resultados = await cu.ejecutar(dto)
        return {
            "success": True,
            "data": [r.model_dump() for r in resultados],
            "total": len(resultados)
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post(
    "/sesiones/forzar-cierre/{usuario_id}",
    response_model=Dict[str, Any],
    summary="Forzar cierre de sesiones",
    description="Cierra todas las sesiones activas de un usuario (admin)."
)
async def forzar_cierre_sesiones(
    usuario_id: int,
    repo: AuditoriaSesionesRepository = Depends(get_auditoria_sesiones_repo)
):
    """Fuerza cierre de sesiones de un usuario."""
    try:
        dto = ForzarCierreSesionesDTO(usuario_id=usuario_id)
        cu = ForzarCierreSesionesCU(repo)
        cantidad_cerrada = await cu.ejecutar(dto)
        return {
            "success": True,
            "message": f"Se cerraron {cantidad_cerrada} sesiones",
            "data": {"cantidad_cerrada": cantidad_cerrada}
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# ==============================================================================
# ENDPOINTS: AUDITORÍA DE CAMBIOS
# ==============================================================================

@router.post(
    "/cambios",
    response_model=Dict[str, Any],
    status_code=status.HTTP_201_CREATED,
    summary="Registrar cambio",
    description="Registra un cambio individual en un campo."
)
async def registrar_cambio(
    dto: RegistrarCambioDTO,
    repo: AuditoriaCambiosRepository = Depends(get_auditoria_cambios_repo)
):
    """Registra un cambio individual."""
    try:
        cu = RegistrarCambioCU(repo)
        resultado = await cu.ejecutar(dto)
        return {
            "success": True,
            "message": "Cambio registrado",
            "data": resultado.model_dump()
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post(
    "/cambios/multiples",
    response_model=Dict[str, Any],
    status_code=status.HTTP_201_CREATED,
    summary="Registrar cambios múltiples",
    description="Registra múltiples cambios en una sola operación."
)
async def registrar_cambios_multiples(
    dto: RegistrarCambiosMultiplesDTO,
    repo: AuditoriaCambiosRepository = Depends(get_auditoria_cambios_repo)
):
    """Registra múltiples cambios."""
    try:
        cu = RegistrarCambiosMultiplesCU(repo)
        await cu.ejecutar(dto)
        return {
            "success": True,
            "message": f"{len(dto.cambios)} cambios registrados"
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get(
    "/cambios/accion/{auditoria_accion_id}",
    response_model=Dict[str, Any],
    summary="Listar cambios por acción",
    description="Lista todos los cambios de una acción de auditoría."
)
async def listar_cambios_por_accion(
    auditoria_accion_id: int,
    repo: AuditoriaCambiosRepository = Depends(get_auditoria_cambios_repo)
):
    """Lista cambios de una acción."""
    try:
        dto = ListarCambiosPorAccionDTO(auditoria_accion_id=auditoria_accion_id)
        cu = ListarCambiosCU(repo)
        resultados = await cu.por_accion(dto)
        return {
            "success": True,
            "data": [r.model_dump() for r in resultados],
            "total": len(resultados)
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# ==============================================================================
# ENDPOINTS: AUDITORÍA DE EXPORTACIONES
# ==============================================================================

@router.post(
    "/exportaciones",
    response_model=Dict[str, Any],
    status_code=status.HTTP_201_CREATED,
    summary="Registrar exportación",
    description="Registra una exportación de datos."
)
async def registrar_exportacion(
    dto: RegistrarExportacionDTO,
    repo: AuditoriaExportacionesRepository = Depends(get_auditoria_exportaciones_repo)
):
    """Registra una exportación."""
    try:
        cu = RegistrarExportacionCU(repo)
        resultado = await cu.ejecutar(dto)
        return {
            "success": True,
            "message": "Exportación registrada",
            "data": resultado.model_dump()
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get(
    "/exportaciones/usuario/{usuario_id}",
    response_model=Dict[str, Any],
    summary="Listar exportaciones por usuario",
    description="Lista exportaciones de un usuario específico."
)
async def listar_exportaciones_por_usuario(
    usuario_id: int,
    desde: Optional[datetime] = Query(None),
    hasta: Optional[datetime] = Query(None),
    tipo: Optional[str] = Query(None),
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    repo: AuditoriaExportacionesRepository = Depends(get_auditoria_exportaciones_repo)
):
    """Lista exportaciones de un usuario."""
    try:
        dto = ListarExportacionesPorUsuarioDTO(
            usuario_id=usuario_id,
            desde=desde,
            hasta=hasta,
            tipo=tipo,
            limit=limit,
            offset=offset
        )
        cu = ListarExportacionesCU(repo)
        resultados = await cu.por_usuario(dto)
        return {
            "success": True,
            "data": [r.model_dump() for r in resultados],
            "total": len(resultados)
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get(
    "/exportaciones/sospechosas",
    response_model=Dict[str, Any],
    summary="Detectar exportaciones sospechosas",
    description="Detecta exportaciones masivas que superan umbrales de seguridad."
)
async def detectar_exportaciones_sospechosas(
    umbral_registros: int = Query(default=1000, ge=100, le=100000),
    ventana_horas: int = Query(default=1, ge=1, le=168),
    repo: AuditoriaExportacionesRepository = Depends(get_auditoria_exportaciones_repo)
):
    """Detecta exportaciones sospechosas."""
    try:
        dto = DetectarExportacionesSospechosasDTO(
            umbral_registros=umbral_registros,
            ventana_horas=ventana_horas
        )
        cu = DetectarExportacionesSospechosasCU(repo)
        resultados = await cu.ejecutar(dto)
        return {
            "success": True,
            "data": [r.model_dump() for r in resultados],
            "total": len(resultados)
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# ==============================================================================
# ENDPOINTS: AUDITORÍA DE PROMPTS IA
# ==============================================================================

@router.post(
    "/prompts-ia",
    response_model=Dict[str, Any],
    status_code=status.HTTP_201_CREATED,
    summary="Registrar prompt IA",
    description="Registra una consulta a IA (ChatGPT)."
)
async def registrar_prompt_ia(
    dto: RegistrarPromptIADTO,
    repo: AuditoriaPromptsIARepository = Depends(get_auditoria_prompts_ia_repo)
):
    """Registra un prompt IA."""
    try:
        cu = RegistrarPromptIACU(repo)
        resultado = await cu.ejecutar(dto)
        return {
            "success": True,
            "message": "Prompt IA registrado",
            "data": resultado.model_dump()
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get(
    "/prompts-ia/usuario/{usuario_id}",
    response_model=Dict[str, Any],
    summary="Listar prompts por usuario",
    description="Lista consultas a IA de un usuario específico."
)
async def listar_prompts_por_usuario(
    usuario_id: int,
    desde: Optional[datetime] = Query(None),
    hasta: Optional[datetime] = Query(None),
    categoria: Optional[str] = Query(None),
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    repo: AuditoriaPromptsIARepository = Depends(get_auditoria_prompts_ia_repo)
):
    """Lista prompts de un usuario."""
    try:
        dto = ListarPromptsPorUsuarioDTO(
            usuario_id=usuario_id,
            desde=desde,
            hasta=hasta,
            categoria=categoria,
            limit=limit,
            offset=offset
        )
        cu = ListarPromptsIACU(repo)
        resultados = await cu.por_usuario(dto)
        return {
            "success": True,
            "data": [r.model_dump() for r in resultados],
            "total": len(resultados)
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get(
    "/prompts-ia/consumo/tokens",
    response_model=Dict[str, Any],
    summary="Calcular tokens consumidos",
    description="Calcula total de tokens consumidos por IA."
)
async def calcular_tokens_consumidos(
    usuario_id: Optional[int] = Query(None),
    sede_id: Optional[int] = Query(None),
    desde: Optional[datetime] = Query(None),
    hasta: Optional[datetime] = Query(None),
    repo: AuditoriaPromptsIARepository = Depends(get_auditoria_prompts_ia_repo)
):
    """Calcula tokens consumidos."""
    try:
        dto = CalcularTokensConsumidosDTO(
            usuario_id=usuario_id,
            sede_id=sede_id,
            desde=desde,
            hasta=hasta
        )
        cu = CalcularConsumoIACU(repo)
        resultado = await cu.tokens_consumidos(dto)
        return {
            "success": True,
            "data": resultado
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get(
    "/prompts-ia/consumo/costo",
    response_model=Dict[str, Any],
    summary="Calcular costo total",
    description="Calcula costo total en USD del uso de IA."
)
async def calcular_costo_total(
    usuario_id: Optional[int] = Query(None),
    sede_id: Optional[int] = Query(None),
    desde: Optional[datetime] = Query(None),
    hasta: Optional[datetime] = Query(None),
    repo: AuditoriaPromptsIARepository = Depends(get_auditoria_prompts_ia_repo)
):
    """Calcula costo total."""
    try:
        dto = CalcularCostoTotalDTO(
            usuario_id=usuario_id,
            sede_id=sede_id,
            desde=desde,
            hasta=hasta
        )
        cu = CalcularConsumoIACU(repo)
        costo = await cu.costo_total(dto)
        return {
            "success": True,
            "data": {"costo_total_usd": costo}
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

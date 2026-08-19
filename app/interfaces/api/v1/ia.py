# app/interfaces/api/v1/ia.py

from __future__ import annotations
from typing import Dict, Any, Optional, List
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.session import get_session

# Repositorio infra
from app.infrastructure.db.repositories.ia import IAConsultasRepository

# Casos de uso
from app.kernel.application.ia import (
    ConsultarIACU,
    ConsultarIADTO,
    ConsultarIAResponse,
    ListarConsultasCU,
    ListarConsultasPorUsuarioDTO,
    ListarConsultasPorProveedorDTO,
    ObtenerConsultaIACU,
    CalcularConsumoIACU,
    CalcularConsumoIADTO,
    ListarModelosCU,
    ListarProveedoresModelosResponse,
    ProbarConexionIACU,
    ProbarConexionIAResponse,
)

# Proveedores IA (MCP) – implementación concreta
from app.infrastructure.services.ia import get_ia_providers, get_ia_provider_by_name

# Errores de dominio
from app.kernel.domain.ia import (
    IAError,
    ConsultaIANoEncontrada,
    ProveedorIANoDisponible,
    ModeloIANoDisponible,
)


router = APIRouter(prefix="/ia", tags=["IA"])


# ============================================================================
# Dependencias
# ============================================================================

def get_ia_repo(db: AsyncSession = Depends(get_session)) -> IAConsultasRepository:
    return IAConsultasRepository(db)


def get_default_provider():
    """
    Devuelve el proveedor por defecto (por ejemplo, desde config).
    Si quieres que el cliente elija proveedor, se usa get_ia_provider_by_name
    dentro del endpoint.
    """
    providers = get_ia_providers()
    if not providers:
        raise ProveedorIANoDisponible("ninguno")
    # Por ahora devolvemos el primero como default
    return providers[0]


# ============================================================================
# Endpoints principales
# ============================================================================

@router.post(
    "/consultas",
    response_model=Dict[str, Any],
    status_code=status.HTTP_201_CREATED,
    summary="Realizar consulta IA",
    description="Realiza una consulta a IA (proveedor agnóstico) y registra la interacción.",
)
async def consultar_ia(
    body: ConsultarIADTO,
    db_repo: IAConsultasRepository = Depends(get_ia_repo),
):
    """
    Endpoint principal para consultar IA.
    El proveedor se toma de body.proveedor (openai, perplexity, gemini, grok, etc.).
    """
    try:
        provider = get_ia_provider_by_name(body.proveedor)
        if provider is None:
            raise ProveedorIANoDisponible(body.proveedor)

        cu = ConsultarIACU(repo=db_repo, provider=provider)
        result: ConsultarIAResponse = await cu.ejecutar(body)

        return {
            "success": True,
            "data": result.consulta.model_dump(),
            "metadata": result.metadata_proveedor,
        }
    except (IAError, ProveedorIANoDisponible, ModeloIANoDisponible) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.mensaje,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get(
    "/consultas/{consulta_id}",
    response_model=Dict[str, Any],
    summary="Obtener detalle de consulta IA",
    description="Obtiene el detalle de una consulta IA por su ID.",
)
async def obtener_consulta_ia(
    consulta_id: int,
    db_repo: IAConsultasRepository = Depends(get_ia_repo),
):
    try:
        cu = ObtenerConsultaIACU(db_repo)
        consulta = await cu.ejecutar(consulta_id)
        return {
            "success": True,
            "data": consulta.model_dump(),
        }
    except ConsultaIANoEncontrada as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.mensaje,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get(
    "/consultas/usuario/{usuario_id}",
    response_model=Dict[str, Any],
    summary="Listar consultas IA por usuario",
    description="Lista las consultas IA realizadas por un usuario.",
)
async def listar_consultas_por_usuario(
    usuario_id: int,
    proveedor: Optional[str] = Query(None),
    desde: Optional[datetime] = Query(None),
    hasta: Optional[datetime] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db_repo: IAConsultasRepository = Depends(get_ia_repo),
):
    try:
        dto = ListarConsultasPorUsuarioDTO(
            usuario_id=usuario_id,
            proveedor=proveedor,
            desde=desde,
            hasta=hasta,
            limit=limit,
            offset=offset,
        )
        cu = ListarConsultasCU(db_repo)
        consultas = await cu.por_usuario(dto)
        return {
            "success": True,
            "data": [c.model_dump() for c in consultas],
            "total": len(consultas),
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get(
    "/consultas/proveedor/{proveedor}",
    response_model=Dict[str, Any],
    summary="Listar consultas IA por proveedor",
    description="Lista las consultas IA realizadas a un proveedor específico.",
)
async def listar_consultas_por_proveedor(
    proveedor: str,
    desde: Optional[datetime] = Query(None),
    hasta: Optional[datetime] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    db_repo: IAConsultasRepository = Depends(get_ia_repo),
):
    try:
        dto = ListarConsultasPorProveedorDTO(
            proveedor=proveedor,
            desde=desde,
            hasta=hasta,
            limit=limit,
        )
        cu = ListarConsultasCU(db_repo)
        consultas = await cu.por_proveedor(dto)
        return {
            "success": True,
            "data": [c.model_dump() for c in consultas],
            "total": len(consultas),
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get(
    "/consumo",
    response_model=Dict[str, Any],
    summary="Calcular consumo IA",
    description="Calcula consumo de tokens y costo para IA (por usuario/proveedor).",
)
async def calcular_consumo_ia(
    usuario_id: Optional[int] = Query(None),
    proveedor: Optional[str] = Query(None),
    desde: Optional[datetime] = Query(None),
    hasta: Optional[datetime] = Query(None),
    db_repo: IAConsultasRepository = Depends(get_ia_repo),
):
    try:
        dto = CalcularConsumoIADTO(
            usuario_id=usuario_id,
            proveedor=proveedor,
            desde=desde,
            hasta=hasta,
        )
        cu = CalcularConsumoIACU(db_repo)
        data = await cu.ejecutar(dto)
        return {
            "success": True,
            "data": data,
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


# ============================================================================
# Endpoints de configuración / diagnóstico MCP
# ============================================================================

@router.get(
    "/modelos",
    response_model=Dict[str, Any],
    summary="Listar proveedores y modelos IA",
    description="Lista los proveedores IA disponibles y sus modelos.",
)
async def listar_modelos_ia():
    try:
        providers = get_ia_providers()
        cu = ListarModelosCU(providers)
        resp: ListarProveedoresModelosResponse = await cu.ejecutar()
        return {
            "success": True,
            "data": resp.model_dump(),
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get(
    "/health",
    response_model=Dict[str, Any],
    summary="Probar conexión a proveedores IA",
    description="Verifica el estado de los proveedores IA configurados.",
)
async def probar_conexion_ia():
    try:
        providers = get_ia_providers()
        cu = ProbarConexionIACU(providers)
        resp: ProbarConexionIAResponse = await cu.ejecutar()
        return {
            "success": True,
            "data": resp.model_dump(),
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )

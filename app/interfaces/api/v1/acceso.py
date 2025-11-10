# app/interfaces/api/v1/acceso/acceso.py
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

# DI genérica
from app.interfaces.api.v1.deps import get_session, get_auditoria_repo

# Adaptador UoW simple para Acceso sobre la sesión, si ya tienes uno propio impórtalo
from app.infrastructure.db.uow import UnitOfWork as DbUoW

# Casos de uso
from app.kernel.application.acceso.generar_codigo import GenerarCodigo, GenerarCodigoRequest, GenerarCodigoResponse
from app.kernel.application.acceso.consumir_codigo import ConsumirCodigo, ConsumirCodigoRequest
from app.kernel.application.acceso.revocar_codigo import RevocarCodigo, RevocarCodigoRequest
from app.kernel.application.acceso.reactivar_codigo import ReactivarCodigo, ReactivarCodigoRequest
from app.kernel.application.acceso.obtener_por_valor import (
    ObtenerCodigoPorValor, ObtenerCodigoPorValorRequest, ObtenerCodigoPorValorResponse
)
from app.kernel.application.acceso.listar_por_sede import (
    ListarCodigosPorSede, ListarCodigosPorSedeRequest, ListarCodigosPorSedeResponse
)
from app.kernel.application.acceso.disponible_codigo import (
    DisponibilidadCodigo, DisponibilidadCodigoRequest, DisponibilidadCodigoResponse
)
from app.kernel.application.acceso.marcar_envio_whatsapp import (
    MarcarEnvioWhatsapp, MarcarEnvioWhatsappRequest
)

from app.kernel.application.acceso.enviar_codigo_whatsapp import (
    EnviarCodigoWhatsapp, EnviarCodigoWhatsappRequest, EnviarCodigoWhatsappResponse
)


# Errores de dominio
from app.kernel.domain.acceso.errors import (
    CodigoNoEncontrado,
    CodigoExpirado,
    CodigoRevocado,
    CodigoAgotado,
    CodigoInvalido,
)

router = APIRouter(prefix="/acceso/codigos", tags=["Acceso"])

def _uow(session: AsyncSession) -> DbUoW:
    return DbUoW(session)

@router.post("/generar", response_model=GenerarCodigoResponse, status_code=status.HTTP_201_CREATED)
async def generar(
    body: GenerarCodigoRequest,
    request: Request,
    session: AsyncSession = Depends(get_session),
    auditoria = Depends(get_auditoria_repo),
):
    cu = GenerarCodigo(_uow(session), auditoria=auditoria)
    return await cu.execute(body)

@router.post("/consumir", status_code=status.HTTP_204_NO_CONTENT)
async def consumir(
    body: ConsumirCodigoRequest,
    request: Request,
    session: AsyncSession = Depends(get_session),
    auditoria = Depends(get_auditoria_repo),
):
    cu = ConsumirCodigo(_uow(session), auditoria=auditoria)
    try:
        await cu.execute(body)
    except (CodigoNoEncontrado, CodigoExpirado, CodigoRevocado, CodigoAgotado) as e:
        # 404 para no encontrado, 409 para estado inválido/agotado/expirado
        code = 404 if isinstance(e, CodigoNoEncontrado) else 409
        raise HTTPException(status_code=code, detail=str(e) or e.__class__.__name__)

@router.post("/revocar", status_code=status.HTTP_204_NO_CONTENT)
async def revocar(
    body: RevocarCodigoRequest,
    session: AsyncSession = Depends(get_session),
    auditoria = Depends(get_auditoria_repo),
):
    cu = RevocarCodigo(_uow(session), auditoria=auditoria)
    try:
        await cu.execute(body)
    except CodigoNoEncontrado as e:
        raise HTTPException(status_code=404, detail=str(e) or "Código no encontrado")

@router.post("/reactivar", status_code=status.HTTP_204_NO_CONTENT)
async def reactivar(
    body: ReactivarCodigoRequest,
    session: AsyncSession = Depends(get_session),
):
    cu = ReactivarCodigo(_uow(session))
    try:
        await cu.execute(body)
    except CodigoNoEncontrado as e:
        raise HTTPException(status_code=404, detail=str(e) or "Código no encontrado")

@router.get("/valor/{valor}", response_model=ObtenerCodigoPorValorResponse)
async def obtener_por_valor(
    valor: str,
    session: AsyncSession = Depends(get_session),
):
    cu = ObtenerCodigoPorValor(_uow(session))
    try:
        return await cu.execute(ObtenerCodigoPorValorRequest(valor=valor))
    except (CodigoNoEncontrado, CodigoInvalido) as e:
        raise HTTPException(status_code=404 if isinstance(e, CodigoNoEncontrado) else 422, detail=str(e) or e.__class__.__name__)

@router.get("/sede/{sede_id}", response_model=ListarCodigosPorSedeResponse)
async def listar_por_sede(
    sede_id: int,
    limit: int = 100,
    offset: int = 0,
    session: AsyncSession = Depends(get_session),
):
    cu = ListarCodigosPorSede(_uow(session))
    req = ListarCodigosPorSedeRequest(sede_id=sede_id, limit=limit, offset=offset)
    return await cu.execute(req)

@router.get("/disponible/{valor}", response_model=DisponibilidadCodigoResponse)
async def disponible(
    valor: str,
    session: AsyncSession = Depends(get_session),
):
    cu = DisponibilidadCodigo(_uow(session))
    return await cu.execute(DisponibilidadCodigoRequest(valor=valor))

@router.post("/enviar/whatsapp", response_model=EnviarCodigoWhatsappResponse, status_code=status.HTTP_200_OK)
async def enviar_whatsapp(
    body: EnviarCodigoWhatsappRequest,
    session: AsyncSession = Depends(get_session),
    auditoria = Depends(get_auditoria_repo),
):
    cu = EnviarCodigoWhatsapp(_uow(session), auditoria=auditoria)
    try:
        return await cu.execute(body)
    except CodigoNoEncontrado as e:
        raise HTTPException(status_code=404, detail=str(e) or "Código no encontrado")
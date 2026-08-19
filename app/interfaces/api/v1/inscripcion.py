# app/interfaces/api/v1/inscripcion.py
from __future__ import annotations

from typing import Optional, Dict, Any, List
from datetime import date
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status, Body, Query, Request
from pydantic import BaseModel, Field

# Casos de uso (agregador de application)
from app.kernel.application.inscripcion import (
    # Formularios
    IniciarInscripcionUseCase, IniciarInscripcionCommand,
    GuardarRespuestasSeccionUseCase, GuardarRespuestasSeccionCommand,
    EnviarFormularioUseCase, EnviarFormularioCommand,
    MarcarRevisadoUseCase, MarcarRevisadoCommand,
    MarcarAprobadoUseCase, MarcarAprobadoCommand,
    RechazarFormularioUseCase, RechazarFormularioCommand,
    ReabrirFormularioUseCase, ReabrirFormularioCommand,
    PreseleccionarTurnoUseCase, PreseleccionarTurnoCommand,
    ObtenerFormularioConsolidadoUseCase, ObtenerFormularioConsolidadoQuery, FormularioConsolidadoDTO,
    BandejaRevisionUseCase, BandejaRevisionQuery,
    ListarHistoricoDireccionUseCase, ListarHistoricoDireccionQuery,
    ListarHistoricoTutorUseCase, ListarHistoricoTutorQuery,
    ValidarPrevAprobarUseCase, ValidarPrevAprobarCommand, ResultadoValidacion,
    # Documentos
    SubirDocumentoInscripcionUseCase, SubirDocumentoCommand,
    ListarDocumentosUseCase, ListarDocumentosQuery,
    ListarDocumentosEstadoUseCase, ListarDocumentosEstadoQuery, DocumentoEstadoDTO,
    ReprocesarDocumentoUseCase, ReprocesarDocumentoCommand,
    EliminarDocumentoUseCase, EliminarDocumentoCommand,
    ReemplazarDocumentoUseCase, ReemplazarDocumentoCommand,
    MarcarDocumentoMarcadoUseCase, MarcarDocumentoMarcadoCommand,
    MarcarDocumentoErrorUseCase, MarcarDocumentoErrorCommand,
    # Firmas
    RegistrarFirmaUseCase, RegistrarFirmaCommand,
    ListarFirmasUseCase, ListarFirmasQuery,
    # Turnos y cotización
    ListarTurnosPorSedeUseCase, ListarTurnosPorSedeQuery,
    CotizarInscripcionUseCase, CotizarInscripcionCommand,
    # Contratos
    ConfirmarInscripcionUseCase, ConfirmarInscripcionCommand,
    RegenerarContratoPdfUseCase, RegenerarContratoPdfCommand,
    # Alta académica y estado de cuenta
    AltaAcademicaUseCase, AltaAcademicaCommand,
    GenerarCargosInicialesUseCase, GenerarCargosInicialesCommand,
    ObtenerEstadoCuentaNinoUseCase, ObtenerEstadoCuentaQuery,
)

# Inyección de dependencias (ejemplos con AsyncSession y repos/servicios)
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.db.session import get_session

# Adapters a puertos (repos y servicios) - debes mapear los concretos aquí
from app.infrastructure.db.repositories.inscripcion.formularios_repo import FormulariosRepository as FormulariosRepoAdapter
from app.infrastructure.db.repositories.inscripcion.formularios_inscripcion_repo import FormularioInscripcionRepository as FormularioInscripcionRepoAdapter
from app.infrastructure.db.repositories.inscripcion.formularios_respuestas_repo import FormularioRespuestaRepository as FormularioRespuestaRepoAdapter
from app.infrastructure.db.repositories.inscripcion.documentos_inscripcion_repo import DocumentoInscripcionRepository as DocumentoRepoAdapter
from app.infrastructure.db.repositories.inscripcion.firmas_repo import FirmaRepository as FirmaRepoAdapter
from app.infrastructure.db.repositories.inscripcion.contratos_repo import ContratoRepository as ContratoRepoAdapter

# Puertos externos (protocols) a implementar en infraestructura/servicios
# Debes proveer implementaciones reales y enlazarlas aquí
class CodigoAccesoService:
    async def validar_y_consumir(self, codigo: str, alumno_id: int, sede_id: int) -> bool:
        # TODO: integrar con /api/v1/acceso
        return True

class WatermarkService:
    async def encolar_marca_agua(self, documento_id: int) -> None:
        # TODO: integrar con cola Celery/RQ
        return None

class PdfGeneratorService:
    async def generar_contrato_pdf(self, contrato_id: int, plantilla_version: Optional[int], variables: Dict[str, Any]) -> str:
        # TODO: generar PDF y devolver ruta local
        return f"/storage/contratos/{contrato_id}.pdf"

class EstadoCuentaService:
    async def crear_cargo(self, alumno_id: int, fecha: date, categoria_pago_id: Optional[int], monto: Decimal, referencia: str, observaciones: Optional[str]) -> int:
        # TODO: integrar con módulo finanzas/estado de cuenta
        return 1

class AsignacionAcademicaService:
    async def asignar_grupo_paralelo(self, alumno_id: int, sede_id: int, edad_meses: int) -> dict:
        # TODO: integrar con módulo académico
        return {"grupo_id": 1, "paralelo_id": 1}


router = APIRouter(prefix="/inscripcion", tags=["Inscripción"])


# Helpers para construir casos de uso con repos/servicios concretos
def get_repos(session: AsyncSession):
    return {
        "form_repo": FormularioInscripcionRepoAdapter(session),
        "resp_repo": FormularioRespuestaRepoAdapter(session),
        "doc_repo": DocumentoRepoAdapter(session),
        "firma_repo": FirmaRepoAdapter(session),
        "contrato_repo": ContratoRepoAdapter(session),
        # FormulariosRepository si necesitas consultas agregadas
        "forms_query_repo": FormulariosRepoAdapter(session),
    }

def get_services():
    return {
        "codigo_service": CodigoAccesoService(),
        "wm_service": WatermarkService(),
        "pdf_service": PdfGeneratorService(),
        "estado_cuenta_service": EstadoCuentaService(),
        "asignacion_service": AsignacionAcademicaService(),
    }


# 1) Inicio y formularios (multipaso y flujos)
@router.post("/iniciar", status_code=201)
async def iniciar_inscripcion(payload: IniciarInscripcionCommand, session: AsyncSession = Depends(get_session)):
    deps = get_repos(session) | get_services()
    uc = IniciarInscripcionUseCase(deps["form_repo"], deps["codigo_service"])
    return await uc.execute(payload)

@router.get("/formularios/{formulario_id}/consolidado", response_model=FormularioConsolidadoDTO)
async def obtener_formulario_consolidado(formulario_id: int, session: AsyncSession = Depends(get_session)):
    deps = get_repos(session)
    uc = ObtenerFormularioConsolidadoUseCase(deps["form_repo"], deps["resp_repo"], deps["doc_repo"], deps["firma_repo"])
    return await uc.execute(ObtenerFormularioConsolidadoQuery(formulario_id=formulario_id))

class GuardarSeccionDTO(BaseModel):
    sede_id: int
    seccion: str = Field(min_length=1, max_length=40)
    datos: Dict[str, Any]

@router.post("/formularios/{formulario_id}/respuestas")
async def guardar_respuestas_seccion(formulario_id: int, body: GuardarSeccionDTO, session: AsyncSession = Depends(get_session)):
    deps = get_repos(session)
    uc = GuardarRespuestasSeccionUseCase(deps["form_repo"], deps["resp_repo"])
    await uc.execute(GuardarRespuestasSeccionCommand(formulario_id=formulario_id, sede_id=body.sede_id, seccion=body.seccion, datos=body.datos))
    return {"ok": True}

@router.post("/formularios/{formulario_id}/enviar")
async def enviar_formulario(formulario_id: int, session: AsyncSession = Depends(get_session)):
    deps = get_repos(session)
    uc = EnviarFormularioUseCase(deps["form_repo"])
    await uc.execute(EnviarFormularioCommand(formulario_id=formulario_id))
    return {"ok": True}

class RevisarDTO(BaseModel):
    usuario_id: int

@router.post("/formularios/{formulario_id}/revisar")
async def marcar_revisado(formulario_id: int, body: RevisarDTO, session: AsyncSession = Depends(get_session)):
    deps = get_repos(session)
    uc = MarcarRevisadoUseCase(deps["form_repo"])
    await uc.execute(MarcarRevisadoCommand(formulario_id=formulario_id, usuario_id=body.usuario_id))
    return {"ok": True}

@router.post("/formularios/{formulario_id}/aprobar")
async def marcar_aprobado(formulario_id: int, body: RevisarDTO, session: AsyncSession = Depends(get_session)):
    deps = get_repos(session)
    uc = MarcarAprobadoUseCase(deps["form_repo"])
    await uc.execute(MarcarAprobadoCommand(formulario_id=formulario_id, usuario_id=body.usuario_id))
    return {"ok": True}

class RechazarDTO(BaseModel):
    observaciones: Optional[str] = None

@router.post("/formularios/{formulario_id}/rechazar")
async def rechazar_formulario(formulario_id: int, body: RechazarDTO, session: AsyncSession = Depends(get_session)):
    deps = get_repos(session)
    uc = RechazarFormularioUseCase(deps["form_repo"])
    await uc.execute(RechazarFormularioCommand(formulario_id=formulario_id, observaciones=body.observaciones))
    return {"ok": True}

class ReabrirDTO(BaseModel):
    destino: str = Field(pattern="^(enviado|borrador)$")
    observaciones: Optional[str] = None

@router.post("/formularios/{formulario_id}/reabrir")
async def reabrir_formulario(formulario_id: int, body: ReabrirDTO, session: AsyncSession = Depends(get_session)):
    deps = get_repos(session)
    uc = ReabrirFormularioUseCase(deps["form_repo"])
    await uc.execute(ReabrirFormularioCommand(formulario_id=formulario_id, destino=body.destino, observaciones=body.observaciones))
    return {"ok": True}

class PreseleccionarTurnoDTO(BaseModel):
    turno_id: int

@router.post("/formularios/{formulario_id}/preseleccionar-turno")
async def preseleccionar_turno(formulario_id: int, body: PreseleccionarTurnoDTO, session: AsyncSession = Depends(get_session)):
    deps = get_repos(session)
    uc = PreseleccionarTurnoUseCase(deps["form_repo"])
    await uc.execute(PreseleccionarTurnoCommand(formulario_id=formulario_id, turno_id=body.turno_id))
    return {"ok": True}

@router.get("/bandeja")
async def bandeja_revision(sede_id: int = Query(...), gestion: Optional[int] = Query(None), limit: int = 50, offset: int = 0, session: AsyncSession = Depends(get_session)):
    deps = get_repos(session)
    uc = BandejaRevisionUseCase(deps["forms_query_repo"])
    return await uc.execute(BandejaRevisionQuery(sede_id=sede_id, gestion=gestion, limit=limit, offset=offset))

@router.get("/historico/direccion")
async def historico_direccion(sede_id: int, gestion: int, limit: int = 50, offset: int = 0, session: AsyncSession = Depends(get_session)):
    deps = get_repos(session)
    uc = ListarHistoricoDireccionUseCase(deps["forms_query_repo"])
    return await uc.execute(ListarHistoricoDireccionQuery(sede_id=sede_id, gestion=gestion, limit=limit, offset=offset))

@router.get("/historico/tutor/{alumno_id}")
async def historico_tutor(alumno_id: int, limit: int = 50, offset: int = 0, session: AsyncSession = Depends(get_session)):
    deps = get_repos(session)
    uc = ListarHistoricoTutorUseCase(deps["forms_query_repo"])
    return await uc.execute(ListarHistoricoTutorQuery(alumno_id=alumno_id, limit=limit, offset=offset))


# 2) Documentos
class SubirDocumentoDTO(SubirDocumentoCommand):
    pass

@router.post("/formularios/{formulario_id}/documentos", status_code=201)
async def subir_documento(formulario_id: int, body: SubirDocumentoDTO, session: AsyncSession = Depends(get_session)):
    deps = get_repos(session) | get_services()
    uc = SubirDocumentoInscripcionUseCase(deps["doc_repo"], deps["wm_service"])
    cmd = SubirDocumentoCommand(formulario_id=formulario_id, **body.model_dump(exclude={"formulario_id"}))
    return await uc.execute(cmd)

@router.get("/formularios/{formulario_id}/documentos")
async def listar_documentos(formulario_id: int, session: AsyncSession = Depends(get_session)):
    deps = get_repos(session)
    uc = ListarDocumentosUseCase(deps["doc_repo"])
    return await uc.execute(ListarDocumentosQuery(formulario_id=formulario_id))

class DocumentosEstadoDTO(BaseModel):
    tipos_requeridos: List[str]

@router.post("/formularios/{formulario_id}/documentos/estado")
async def documentos_estado(formulario_id: int, body: DocumentosEstadoDTO, session: AsyncSession = Depends(get_session)):
    deps = get_repos(session)
    uc = ListarDocumentosEstadoUseCase(deps["doc_repo"])
    return await uc.execute(ListarDocumentosEstadoQuery(formulario_id=formulario_id, tipos_requeridos=body.tipos_requeridos))

@router.post("/documentos/{documento_id}/reprocesar")
async def reprocesar_documento(documento_id: int, session: AsyncSession = Depends(get_session)):
    deps = get_repos(session) | get_services()
    uc = ReprocesarDocumentoUseCase(deps["doc_repo"], deps["wm_service"])
    await uc.execute(ReprocesarDocumentoCommand(documento_id=documento_id))
    return {"ok": True}

class ReemplazarDocumentoDTO(ReemplazarDocumentoCommand):
    pass

@router.post("/documentos/{documento_id}/reemplazar")
async def reemplazar_documento(documento_id: int, body: ReemplazarDocumentoDTO, session: AsyncSession = Depends(get_session)):
    deps = get_repos(session) | get_services()
    uc = ReemplazarDocumentoUseCase(deps["doc_repo"], deps["wm_service"])
    await uc.execute(ReemplazarDocumentoCommand(documento_id=documento_id, **body.model_dump(exclude={"documento_id"})))
    return {"ok": True}

@router.delete("/documentos/{documento_id}")
async def eliminar_documento(documento_id: int, session: AsyncSession = Depends(get_session)):
    deps = get_repos(session)
    uc = EliminarDocumentoUseCase(deps["doc_repo"])
    await uc.execute(EliminarDocumentoCommand(documento_id=documento_id))
    return {"ok": True}

# Callbacks del worker (opcional proteger con token interno)
class DocMarcadoDTO(BaseModel):
    watermark_url: str

@router.post("/documentos/{documento_id}/marcado")
async def marcar_documento_marcado(documento_id: int, body: DocMarcadoDTO, session: AsyncSession = Depends(get_session)):
    deps = get_repos(session)
    uc = MarcarDocumentoMarcadoUseCase(deps["doc_repo"])
    await uc.execute(MarcarDocumentoMarcadoCommand(documento_id=documento_id, watermark_url=body.watermark_url))
    return {"ok": True}

class DocErrorDTO(BaseModel):
    error: str

@router.post("/documentos/{documento_id}/error")
async def marcar_documento_error(documento_id: int, body: DocErrorDTO, session: AsyncSession = Depends(get_session)):
    deps = get_repos(session)
    uc = MarcarDocumentoErrorUseCase(deps["doc_repo"])
    await uc.execute(MarcarDocumentoErrorCommand(documento_id=documento_id, error=body.error))
    return {"ok": True}


# 3) Firmas
class RegistrarFirmaDTO(RegistrarFirmaCommand):
    pass

@router.post("/formularios/{formulario_id}/firmas", status_code=201)
async def registrar_firma(formulario_id: int, body: RegistrarFirmaDTO, session: AsyncSession = Depends(get_session)):
    deps = get_repos(session)
    uc = RegistrarFirmaUseCase(deps["firma_repo"])
    cmd = RegistrarFirmaCommand(formulario_id=formulario_id, **body.model_dump(exclude={"formulario_id"}))
    return await uc.execute(cmd)

@router.get("/formularios/{formulario_id}/firmas")
async def listar_firmas(formulario_id: int, session: AsyncSession = Depends(get_session)):
    deps = get_repos(session)
    uc = ListarFirmasUseCase(deps["firma_repo"])
    return await uc.execute(ListarFirmasQuery(formulario_id=formulario_id))


# 4) Turnos y cotización
@router.get("/turnos/{sede_id}")
async def listar_turnos(sede_id: int, gestion: int = Query(...), categoria_pago_id: Optional[int] = None, session: AsyncSession = Depends(get_session)):
    # TODO: inyectar repos reales de turnos/precios
    turnos_repo = None  # implementar adapter
    precios_repo = None  # implementar adapter
    uc = ListarTurnosPorSedeUseCase(turnos_repo, precios_repo)
    return await uc.execute(ListarTurnosPorSedeQuery(sede_id=sede_id, gestion=gestion, categoria_pago_id=categoria_pago_id))

class CotizarDTO(CotizarInscripcionCommand):
    pass

@router.post("/cotizar")
async def cotizar_inscripcion(body: CotizarDTO, session: AsyncSession = Depends(get_session)):
    # TODO: inyectar repos reales de precios
    precios_repo = None  # implementar adapter
    uc = CotizarInscripcionUseCase(precios_repo)
    return await uc.execute(body)


# 5) Contratos
class ConfirmarDTO(ConfirmarInscripcionCommand):
    pass

@router.post("/confirmar")
async def confirmar_inscripcion(body: ConfirmarDTO, session: AsyncSession = Depends(get_session)):
    deps = get_repos(session) | get_services()
    uc = ConfirmarInscripcionUseCase(deps["form_repo"], deps["contrato_repo"], deps["pdf_service"])
    return await uc.execute(body)

class RegenerarContratoDTO(RegenerarContratoPdfCommand):
    pass

@router.post("/contratos/regenerar")
async def regenerar_contrato(body: RegenerarContratoDTO, session: AsyncSession = Depends(get_session)):
    deps = get_repos(session) | get_services()
    uc = RegenerarContratoPdfUseCase(deps["contrato_repo"], deps["pdf_service"])
    return await uc.execute(body)


# 6) Alta académica y estado de cuenta
class AltaAcademicaDTO(AltaAcademicaCommand):
    pass

@router.post("/alta-academica")
async def alta_academica(body: AltaAcademicaDTO, session: AsyncSession = Depends(get_session)):
    deps = get_services()
    uc = AltaAcademicaUseCase(deps["asignacion_service"])
    return await uc.execute(body)

@router.post("/estado-cuenta/cargos-iniciales")
async def generar_cargos_iniciales(body: GenerarCargosInicialesCommand, session: AsyncSession = Depends(get_session)):
    deps = get_services()
    uc = GenerarCargosInicialesUseCase(deps["estado_cuenta_service"])
    return await uc.execute(body)

@router.get("/estado-cuenta/{alumno_id}")
async def obtener_estado_cuenta(alumno_id: int, limit: int = 100, session: AsyncSession = Depends(get_session)):
    # TODO: inyectar repo real de estado de cuenta
    repo = None  # implementar adapter
    uc = ObtenerEstadoCuentaNinoUseCase(repo)
    return await uc.execute(ObtenerEstadoCuentaQuery(alumno_id=alumno_id, limit=limit))

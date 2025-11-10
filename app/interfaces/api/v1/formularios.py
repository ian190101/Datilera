from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from app.interfaces.api.v1.deps import get_uow_dep
from app.infrastructure.db.uow import UnitOfWork
from app.kernel.domain.exceptions import EntityNotFoundException, DuplicatedEntityException

# Repositories
from app.infrastructure.db.repositories.inscripcion.formularios_inscripcion import FormularioInscripcionRepository
from app.infrastructure.db.repositories.inscripcion.formularios_respuestas import FormularioRespuestaRepository
from app.infrastructure.db.repositories.inscripcion.contratos import ContratoRepository
from app.infrastructure.db.repositories.inscripcion.firmas import FirmaRepository
from app.infrastructure.db.repositories.inscripcion.documentos_inscripcion import DocumentoInscripcionRepository
from app.infrastructure.db.repositories.alumnos.alumnos import AlumnoRepository
from app.infrastructure.db.repositories.seguridad.usuarios import UsuarioRepository

# Application Services
from app.kernel.application.inscripcion.crear_formulario import CreateFormulario, CreateFormularioRequest, FormularioResponse
from app.kernel.application.inscripcion.guardar_respuestas import SaveAnswers, SaveAnswersRequest
from app.kernel.application.inscripcion.obtener_formulario import GetFormulario, FormularioDetailResponse
from app.kernel.application.inscripcion.generar_contrato import GenerateContract, GenerateContractResponse
from app.kernel.application.inscripcion.guardar_firma import SaveSignature, SaveSignatureRequest
from app.kernel.application.inscripcion.subir_documento import UploadDocument, UploadDocumentRequest

router = APIRouter(prefix="/formularios", tags=["Formularios de Inscripción"])


@router.post("/", response_model=FormularioResponse, status_code=status.HTTP_201_CREATED)
async def create_formulario(
    request: CreateFormularioRequest,
    uow: UnitOfWork = Depends(get_uow_dep),
):
    """
    Crea un nuevo formulario de inscripción para un alumno.
    """
    try:
        form_repo = FormularioInscripcionRepository(uow.session_required)
        alumno_repo = AlumnoRepository(uow.session_required)
        service = CreateFormulario(form_repo, alumno_repo)
        created_form = await service.execute(request)
        return created_form
    except (EntityNotFoundException, DuplicatedEntityException) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/{form_id}/respuestas", status_code=status.HTTP_204_NO_CONTENT)
async def save_answers(
    form_id: int,
    request: SaveAnswersRequest,
    uow: UnitOfWork = Depends(get_uow_dep),
):
    """
    Guarda las respuestas para un formulario de inscripción.
    """
    try:
        form_repo = FormularioInscripcionRepository(uow.session_required)
        answer_repo = FormularioRespuestaRepository(uow.session_required)
        service = SaveAnswers(form_repo, answer_repo)
        await service.execute(form_id, request)
    except EntityNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.get("/{form_id}", response_model=FormularioDetailResponse)
async def get_formulario(
    form_id: int,
    uow: UnitOfWork = Depends(get_uow_dep),
):
    """
    Obtiene los detalles de un formulario de inscripción, incluyendo sus respuestas.
    """
    try:
        form_repo = FormularioInscripcionRepository(uow.session_required)
        answer_repo = FormularioRespuestaRepository(uow.session_required)
        service = GetFormulario(form_repo, answer_repo)
        form_details = await service.execute(form_id)
        return form_details
    except EntityNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.post("/{form_id}/contrato", response_model=GenerateContractResponse, status_code=status.HTTP_201_CREATED)
async def generate_contract(
    form_id: int,
    uow: UnitOfWork = Depends(get_uow_dep),
):
    """
    Genera el contrato de inscripción en formato PDF.
    """
    try:
        form_repo = FormularioInscripcionRepository(uow.session_required)
        alumno_repo = AlumnoRepository(uow.session_required)
        user_repo = UsuarioRepository(uow.session_required)
        contract_repo = ContratoRepository(uow.session_required)

        service = GenerateContract(form_repo, alumno_repo, user_repo, contract_repo)
        pdf_path = await service.execute(form_id)
        return pdf_path
    except EntityNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.post("/{form_id}/firmas", status_code=status.HTTP_201_CREATED)
async def save_signature(
    form_id: int,
    request: SaveSignatureRequest,
    uow: UnitOfWork = Depends(get_uow_dep),
):
    """
    Guarda una firma digital para un formulario de inscripción.
    """
    try:
        form_repo = FormularioInscripcionRepository(uow.session_required)
        signature_repo = FirmaRepository(uow.session_required)
        service = SaveSignature(form_repo, signature_repo)
        await service.execute(form_id, request)
        return {"message": "Firma guardada correctamente."}
    except EntityNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/{form_id}/documentos", status_code=status.HTTP_201_CREATED)
async def upload_document(
    form_id: int,
    tipo_documento: str = Form(...),
    file: UploadFile = File(...),
    uow: UnitOfWork = Depends(get_uow_dep),
):
    """
    Sube un documento para un formulario de inscripción.
    """
    try:
        form_repo = FormularioInscripcionRepository(uow.session_required)
        doc_repo = DocumentoInscripcionRepository(uow.session_required)
        
        # TODO: Implementar la lógica real de almacenamiento del archivo en el sistema de archivos
        # Por ahora, se simula la URL del archivo guardado
        file_location = f"/documentos/{form_id}/{file.filename}"
        
        # Crear una instancia de UploadDocumentRequest para pasar al servicio
        upload_request = UploadDocumentRequest(
            tipo_documento=tipo_documento,
            file_url=file_location,
            nombre_archivo=file.filename
        )
        
        service = UploadDocument(form_repo, doc_repo)
        await service.execute(form_id, upload_request)
        return {"message": "Documento subido correctamente.", "file_url": file_location}
    except EntityNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al subir el documento: {str(e)}",
        )
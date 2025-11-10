from pydantic import BaseModel
from app.infrastructure.db.repositories.inscripcion.formularios_inscripcion import FormularioInscripcionRepository
from app.infrastructure.db.repositories.inscripcion.documentos_inscripcion import DocumentoInscripcionRepository
from app.kernel.domain.exceptions import EntityNotFoundException
from app.infrastructure.db.models.inscripcion import DocumentoInscripcion


class UploadDocumentRequest(BaseModel):
    tipo_documento: str
    file_url: str  # URL donde se almacena el documento
    nombre_archivo: str


class UploadDocument:
    def __init__(
        self,
        form_repo: FormularioInscripcionRepository,
        doc_repo: DocumentoInscripcionRepository,
    ):
        self.form_repo = form_repo
        self.doc_repo = doc_repo

    async def execute(self, form_id: int, request: UploadDocumentRequest) -> None:
        if not await self.form_repo.get_by_id(form_id):
            raise EntityNotFoundException(f"Formulario con id {form_id} no encontrado.")

        # TODO: Implementar la lógica real de almacenamiento del archivo
        # Por ahora, se asume que file_url ya contiene la URL del archivo guardado

        new_document = DocumentoInscripcion(
            formulario_id=form_id,
            tipo_documento=request.tipo_documento,
            url=request.file_url,
            nombre_archivo=request.nombre_archivo,
        )
        await self.doc_repo.create(new_document)
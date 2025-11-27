from pydantic import BaseModel
from app.kernel.domain.inscripcion import EstadoProcesamientoDocumento
from app.kernel.domain.inscripcion.ports import DocumentoInscripcionRepositoryPort
from app.kernel.domain.inscripcion.errors import DocumentoNoEncontrado, DocumentoProcesamientoInvalido

class MarcarDocumentoErrorCommand(BaseModel):
    documento_id: int
    error: str

class MarcarDocumentoErrorUseCase:
    def __init__(self, doc_repo: DocumentoInscripcionRepositoryPort):
        self.doc_repo = doc_repo

    async def execute(self, cmd: MarcarDocumentoErrorCommand) -> None:
        doc = await self.doc_repo.obtener_por_id(cmd.documento_id)
        if not doc:
            raise DocumentoNoEncontrado(cmd.documento_id)
        if doc.estado_procesamiento.value not in ("procesando", "pendiente"):
            raise DocumentoProcesamientoInvalido(doc.estado_procesamiento.value)
        await self.doc_repo.actualizar_estado(doc.id, EstadoProcesamientoDocumento.ERROR, error=cmd.error, watermark_url=None)

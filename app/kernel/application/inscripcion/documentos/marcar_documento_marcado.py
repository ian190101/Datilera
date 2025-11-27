from pydantic import BaseModel
from app.kernel.domain.inscripcion import EstadoProcesamientoDocumento
from app.kernel.domain.inscripcion.ports import DocumentoInscripcionRepositoryPort
from app.kernel.domain.inscripcion.errors import DocumentoNoEncontrado, DocumentoProcesamientoInvalido

class MarcarDocumentoMarcadoCommand(BaseModel):
    documento_id: int
    watermark_url: str

class MarcarDocumentoMarcadoUseCase:
    def __init__(self, doc_repo: DocumentoInscripcionRepositoryPort):
        self.doc_repo = doc_repo

    async def execute(self, cmd: MarcarDocumentoMarcadoCommand) -> None:
        doc = await self.doc_repo.obtener_por_id(cmd.documento_id)
        if not doc:
            raise DocumentoNoEncontrado(cmd.documento_id)
        # Estrictamente desde PROCESANDO para evitar condiciones de carrera
        if doc.estado_procesamiento.value not in ("procesando",):
            raise DocumentoProcesamientoInvalido(doc.estado_procesamiento.value)
        await self.doc_repo.actualizar_estado(doc.id, EstadoProcesamientoDocumento.MARCADO, error=None, watermark_url=cmd.watermark_url)

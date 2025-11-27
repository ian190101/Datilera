# app/application/inscripcion/documentos/reprocesar_documento.py
from pydantic import BaseModel
from app.kernel.domain.inscripcion import EstadoProcesamientoDocumento
from app.kernel.domain.inscripcion.ports import DocumentoInscripcionRepositoryPort, WatermarkServicePort
from app.kernel.domain.inscripcion.errors import DocumentoNoEncontrado, DocumentoProcesamientoInvalido

class ReprocesarDocumentoCommand(BaseModel):
    documento_id: int

class ReprocesarDocumentoUseCase:
    def __init__(self, doc_repo: DocumentoInscripcionRepositoryPort, wm_service: WatermarkServicePort):
        self.doc_repo = doc_repo
        self.wm_service = wm_service

    async def execute(self, cmd: ReprocesarDocumentoCommand) -> None:
        doc = await self.doc_repo.obtener_por_id(cmd.documento_id)
        if not doc:
            raise DocumentoNoEncontrado(cmd.documento_id)
        if doc.estado_procesamiento.value not in ("pendiente", "error"):
            raise DocumentoProcesamientoInvalido(doc.estado_procesamiento.value)
        await self.doc_repo.actualizar_estado(doc.id, EstadoProcesamientoDocumento.PROCESANDO)
        await self.wm_service.encolar_marca_agua(doc.id)

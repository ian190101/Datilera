# app/application/inscripcion/documentos/eliminar_o_reemplazar_documento.py
from typing import Optional
from pydantic import BaseModel, Field
from app.kernel.domain.inscripcion import EstadoProcesamientoDocumento
from app.kernel.domain.inscripcion.ports import DocumentoInscripcionRepositoryPort, WatermarkServicePort
from app.kernel.domain.inscripcion.errors import DocumentoNoEncontrado, DocumentoProcesamientoInvalido

class EliminarDocumentoCommand(BaseModel):
    documento_id: int

class ReemplazarDocumentoCommand(BaseModel):
    documento_id: int
    nueva_url: str
    nuevo_nombre: str
    mime: Optional[str] = None
    tamano_bytes: Optional[int] = None
    hash_archivo: Optional[str] = Field(default=None, max_length=64)

class EliminarDocumentoUseCase:
    def __init__(self, doc_repo: DocumentoInscripcionRepositoryPort):
        self.doc_repo = doc_repo

    async def execute(self, cmd: EliminarDocumentoCommand) -> None:
        doc = await self.doc_repo.obtener_por_id(cmd.documento_id)
        if not doc:
            raise DocumentoNoEncontrado(cmd.documento_id)
        if doc.estado_procesamiento.value not in ("pendiente", "error"):
            raise DocumentoProcesamientoInvalido(doc.estado_procesamiento.value)
        if hasattr(self.doc_repo, "eliminar"):
            await getattr(self.doc_repo, "eliminar")(doc.id)

class ReemplazarDocumentoUseCase:
    def __init__(self, doc_repo: DocumentoInscripcionRepositoryPort, wm_service: WatermarkServicePort):
        self.doc_repo = doc_repo
        self.wm_service = wm_service

    async def execute(self, cmd: ReemplazarDocumentoCommand) -> None:
        doc = await self.doc_repo.obtener_por_id(cmd.documento_id)
        if not doc:
            raise DocumentoNoEncontrado(cmd.documento_id)
        if doc.estado_procesamiento.value not in ("pendiente", "error"):
            raise DocumentoProcesamientoInvalido(doc.estado_procesamiento.value)
        await self.doc_repo.actualizar_metadata(doc.id, cmd.mime, cmd.tamano_bytes, cmd.hash_archivo)
        if hasattr(self.doc_repo, "actualizar_url_y_nombre"):
            await getattr(self.doc_repo, "actualizar_url_y_nombre")(doc.id, cmd.nueva_url, cmd.nuevo_nombre)
        await self.doc_repo.actualizar_estado(doc.id, EstadoProcesamientoDocumento.PENDIENTE, error=None, watermark_url=None)
        await self.wm_service.encolar_marca_agua(doc.id)

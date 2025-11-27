# app/application/inscripcion/documentos/subir_documento_inscripcion.py
from typing import Optional
from pydantic import BaseModel, Field
from app.kernel.domain.inscripcion import DocumentoInscripcion, EstadoProcesamientoDocumento
from app.kernel.domain.inscripcion.ports import DocumentoInscripcionRepositoryPort, WatermarkServicePort
from app.kernel.domain.inscripcion.errors import ArchivoDuplicadoHash, DocumentoMimeNoPermitido, DocumentoTamanoExcedido

MIMES_PERMITIDOS = {"image/png", "image/jpeg", "application/pdf"}
TAMANO_MAX_BYTES = 15 * 1024 * 1024

class SubirDocumentoCommand(BaseModel):
    formulario_id: int
    tipo_documento: str = Field(min_length=2, max_length=80)
    url: str
    nombre_archivo: str
    mime: Optional[str] = None
    tamano_bytes: Optional[int] = None
    hash_archivo: Optional[str] = Field(default=None, max_length=64)

class SubirDocumentoInscripcionUseCase:
    def __init__(self, doc_repo: DocumentoInscripcionRepositoryPort, wm_service: WatermarkServicePort):
        self.doc_repo = doc_repo
        self.wm_service = wm_service

    async def execute(self, cmd: SubirDocumentoCommand) -> DocumentoInscripcion:
        if cmd.mime and cmd.mime not in MIMES_PERMITIDOS:
            raise DocumentoMimeNoPermitido(cmd.mime)
        if cmd.tamano_bytes and cmd.tamano_bytes > TAMANO_MAX_BYTES:
            raise DocumentoTamanoExcedido(cmd.tamano_bytes, TAMANO_MAX_BYTES)
        if cmd.hash_archivo:
            dup = await self.doc_repo.obtener_por_hash(cmd.hash_archivo)
            if dup:
                raise ArchivoDuplicadoHash(cmd.hash_archivo)

        doc = DocumentoInscripcion(
            id=0,
            formulario_id=cmd.formulario_id,
            tipo_documento=cmd.tipo_documento,
            url=cmd.url,
            nombre_archivo=cmd.nombre_archivo,
            mime=cmd.mime,
            tamano_bytes=cmd.tamano_bytes,
            hash_archivo=cmd.hash_archivo,
            estado_procesamiento=EstadoProcesamientoDocumento.PENDIENTE,
        )
        doc = await self.doc_repo.crear(doc)
        await self.doc_repo.actualizar_metadata(doc.id, cmd.mime, cmd.tamano_bytes, cmd.hash_archivo)
        await self.wm_service.encolar_marca_agua(doc.id)
        return doc

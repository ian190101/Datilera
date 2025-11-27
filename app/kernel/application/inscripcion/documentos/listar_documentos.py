# app/application/inscripcion/documentos/listar_documentos.py
from typing import List
from pydantic import BaseModel
from app.kernel.domain.inscripcion import DocumentoInscripcion
from app.kernel.domain.inscripcion.ports import DocumentoInscripcionRepositoryPort

class ListarDocumentosQuery(BaseModel):
    formulario_id: int

class ListarDocumentosUseCase:
    def __init__(self, doc_repo: DocumentoInscripcionRepositoryPort):
        self.doc_repo = doc_repo

    async def execute(self, q: ListarDocumentosQuery) -> List[DocumentoInscripcion]:
        return await self.doc_repo.listar_por_formulario(q.formulario_id)

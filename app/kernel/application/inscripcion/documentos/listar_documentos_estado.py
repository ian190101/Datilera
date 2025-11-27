from typing import List, Dict, Optional
from pydantic import BaseModel, Field
from app.kernel.domain.inscripcion import DocumentoInscripcion
from app.kernel.domain.inscripcion.ports import DocumentoInscripcionRepositoryPort

class ListarDocumentosEstadoQuery(BaseModel):
    formulario_id: int
    tipos_requeridos: List[str] = Field(min_length=1)

class DocumentoEstadoDTO(BaseModel):
    tipo: str
    completo: bool
    documentos: List[DocumentoInscripcion] = []

class ListarDocumentosEstadoUseCase:
    def __init__(self, doc_repo: DocumentoInscripcionRepositoryPort):
        self.doc_repo = doc_repo

    async def execute(self, q: ListarDocumentosEstadoQuery) -> Dict[str, DocumentoEstadoDTO]:
        cargados = await self.doc_repo.listar_por_formulario(q.formulario_id)
        index: Dict[str, List[DocumentoInscripcion]] = {}
        for d in cargados:
            index.setdefault(d.tipo_documento, []).append(d)
        resultado: Dict[str, DocumentoEstadoDTO] = {}
        for tipo in q.tipos_requeridos:
            lst = index.get(tipo, [])
            resultado[tipo] = DocumentoEstadoDTO(tipo=tipo, completo=len(lst) > 0, documentos=lst)
        # También incluir tipos extra no requeridos (opcionales) ya cargados
        for tipo in index.keys():
            if tipo not in resultado:
                resultado[tipo] = DocumentoEstadoDTO(tipo=tipo, completo=True, documentos=index[tipo])
        return resultado

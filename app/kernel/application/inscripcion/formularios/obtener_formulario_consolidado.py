# app/application/inscripcion/formularios/obtener_formulario_consolidado.py
from typing import Dict, List, Any
from pydantic import BaseModel
from app.kernel.domain.inscripcion import FormularioInscripcion, DocumentoInscripcion, Firma
from app.kernel.domain.inscripcion.ports import (
    FormularioInscripcionRepositoryPort, FormularioRespuestaRepositoryPort,
    DocumentoInscripcionRepositoryPort, FirmaRepositoryPort,
)
from app.kernel.domain.inscripcion.errors import FormularioNoEncontrado

class ObtenerFormularioConsolidadoQuery(BaseModel):
    formulario_id: int

class FormularioConsolidadoDTO(BaseModel):
    formulario: FormularioInscripcion
    respuestas_por_seccion: Dict[str, Dict[str, Any]]
    documentos: List[DocumentoInscripcion]
    firmas: List[Firma]

class ObtenerFormularioConsolidadoUseCase:
    def __init__(self, form_repo: FormularioInscripcionRepositoryPort, resp_repo: FormularioRespuestaRepositoryPort, doc_repo: DocumentoInscripcionRepositoryPort, firma_repo: FirmaRepositoryPort):
        self.form_repo = form_repo
        self.resp_repo = resp_repo
        self.doc_repo = doc_repo
        self.firma_repo = firma_repo

    async def execute(self, q: ObtenerFormularioConsolidadoQuery) -> FormularioConsolidadoDTO:
        form = await self.form_repo.obtener_por_id(q.formulario_id)
        if not form:
            raise FormularioNoEncontrado(q.formulario_id)
        resps = await self.resp_repo.listar_por_formulario(q.formulario_id)
        agrupadas: Dict[str, Dict[str, Any]] = {}
        for r in resps:
            seccion = r.seccion or "general"
            agrupadas.setdefault(seccion, {})
            agrupadas[seccion][r.campo] = r.valor
        docs = await self.doc_repo.listar_por_formulario(q.formulario_id)
        firmas = await self.firma_repo.listar_por_formulario(q.formulario_id)
        return FormularioConsolidadoDTO(formulario=form, respuestas_por_seccion=agrupadas, documentos=docs, firmas=firmas)

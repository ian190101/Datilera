# app/application/inscripcion/contratos/regenerar_contrato.py
from typing import Optional, Dict
from pydantic import BaseModel
from app.kernel.domain.inscripcion.ports import ContratoRepositoryPort, PdfGeneratorServicePort
from app.kernel.domain.inscripcion.errors import ContratoNoEncontrado

class RegenerarContratoPdfCommand(BaseModel):
    formulario_id: int
    plantilla_version: Optional[int] = None
    variables: Dict[str, object]

class RegenerarContratoPdfUseCase:
    def __init__(self, contrato_repo: ContratoRepositoryPort, pdf_service: PdfGeneratorServicePort):
        self.contrato_repo = contrato_repo
        self.pdf_service = pdf_service

    async def execute(self, cmd: RegenerarContratoPdfCommand) -> str:
        contrato = await self.contrato_repo.obtener_por_formulario(cmd.formulario_id)
        if not contrato:
            raise ContratoNoEncontrado(cmd.formulario_id)
        pdf_url = await self.pdf_service.generar_contrato_pdf(contrato.id, cmd.plantilla_version, cmd.variables)
        await self.contrato_repo.actualizar_pdf_url(contrato.id, pdf_url)
        return pdf_url

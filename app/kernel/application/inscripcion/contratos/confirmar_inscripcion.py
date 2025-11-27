# app/application/inscripcion/contratos/confirmar_inscripcion.py
from typing import Dict, Optional
from pydantic import BaseModel
from app.kernel.domain.inscripcion import Contrato
from app.kernel.domain.inscripcion.ports import FormularioInscripcionRepositoryPort, ContratoRepositoryPort, PdfGeneratorServicePort
from app.kernel.domain.inscripcion.errors import FormularioNoEncontrado, NumeracionNoDisponible

class ConfirmarInscripcionCommand(BaseModel):
    formulario_id: int
    sede_id: int
    turno_id: int
    aprobado_por: int
    plantilla_version: Optional[int] = None
    variables: Dict[str, object]

class ConfirmarInscripcionUseCase:
    def __init__(self, form_repo: FormularioInscripcionRepositoryPort, contrato_repo: ContratoRepositoryPort, pdf_service: PdfGeneratorServicePort):
        self.form_repo = form_repo
        self.contrato_repo = contrato_repo
        self.pdf_service = pdf_service

    async def execute(self, cmd: ConfirmarInscripcionCommand) -> Contrato:
        form = await self.form_repo.obtener_por_id(cmd.formulario_id)
        if not form:
            raise FormularioNoEncontrado(cmd.formulario_id)
        await self.form_repo.fijar_turno(cmd.formulario_id, cmd.turno_id)
        await self.form_repo.marcar_aprobado(cmd.formulario_id, cmd.aprobado_por)
        numeracion = await self.contrato_repo.reservar_numeracion(cmd.sede_id)
        if not numeracion:
            raise NumeracionNoDisponible(cmd.sede_id)
        codigo = f"{cmd.sede_id}-{cmd.formulario_id}-{numeracion}"
        contrato = Contrato(id=0, formulario_id=cmd.formulario_id, sede_id=cmd.sede_id,
                            codigo_contrato=codigo, numeracion_sede=numeracion,
                            plantilla_version=cmd.plantilla_version, variables_json=cmd.variables)
        contrato = await self.contrato_repo.crear(contrato)
        pdf_url = await self.pdf_service.generar_contrato_pdf(contrato.id, cmd.plantilla_version, cmd.variables)
        await self.contrato_repo.actualizar_pdf_url(contrato.id, pdf_url)
        return contrato

# app/application/inscripcion/formularios/iniciar_inscripcion.py
from typing import Optional
from pydantic import BaseModel, Field
from app.kernel.domain.inscripcion import FormularioInscripcion
from app.kernel.domain.inscripcion.ports import FormularioInscripcionRepositoryPort, CodigoAccesoServicePort
from app.kernel.domain.inscripcion.errors import CodigoAccesoInvalido

class IniciarInscripcionCommand(BaseModel):
    codigo: str = Field(min_length=6, max_length=6)
    alumno_id: int
    sede_id: int
    gestion: int
    usuario_id: int  # tutor

class IniciarInscripcionUseCase:
    def __init__(self, form_repo: FormularioInscripcionRepositoryPort, codigo_service: CodigoAccesoServicePort):
        self.form_repo = form_repo
        self.codigo_service = codigo_service

    async def execute(self, cmd: IniciarInscripcionCommand) -> FormularioInscripcion:
        ok = await self.codigo_service.validar_y_consumir(cmd.codigo, cmd.alumno_id, cmd.sede_id)
        if not ok:
            raise CodigoAccesoInvalido(cmd.codigo)
        return await self.form_repo.crear(alumno_id=cmd.alumno_id, sede_id=cmd.sede_id, gestion=cmd.gestion)

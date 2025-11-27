# app/application/inscripcion/formularios/marcar_revisado.py
from pydantic import BaseModel
from app.kernel.domain.inscripcion.ports import FormularioInscripcionRepositoryPort
from app.kernel.domain.inscripcion.errors import FormularioNoEncontrado

class MarcarRevisadoCommand(BaseModel):
    formulario_id: int
    usuario_id: int

class MarcarRevisadoUseCase:
    def __init__(self, form_repo: FormularioInscripcionRepositoryPort):
        self.form_repo = form_repo

    async def execute(self, cmd: MarcarRevisadoCommand) -> None:
        form = await self.form_repo.obtener_por_id(cmd.formulario_id)
        if not form:
            raise FormularioNoEncontrado(cmd.formulario_id)
        await self.form_repo.marcar_revisado(cmd.formulario_id, cmd.usuario_id)

# app/kernel/application/auditoria/registrar_evento.py
from __future__ import annotations
from pydantic import BaseModel, ConfigDict
from app.kernel.domain.auditoria.ports import IAuditoriaAccionRepo
from app.kernel.domain.auditoria.auditoria_accion_entidad import AuditoriaAccion

class RegistrarAuditoriaAccionRequest(AuditoriaAccion):
    model_config = ConfigDict(from_attributes=True)

class RegistrarAuditoriaAccion:
    def __init__(self, repo: IAuditoriaAccionRepo):
        self.repo = repo
    async def execute(self, req: RegistrarAuditoriaAccionRequest) -> None:
        await self.repo.registrar(AuditoriaAccion.model_validate(req))

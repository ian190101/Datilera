# app/application/inscripcion/formularios/bandeja_revision.py
from typing import List, Optional, Protocol
from pydantic import BaseModel
from app.kernel.domain.inscripcion import FormularioInscripcion

class BandejaFormularioRepositoryPort(Protocol):
    async def listar_bandeja(self, sede_id: int, gestion: Optional[int], estado: str, limit: int, offset: int) -> List[FormularioInscripcion]: ...

class BandejaRevisionQuery(BaseModel):
    sede_id: int
    gestion: Optional[int] = None
    limit: int = 50
    offset: int = 0

class BandejaRevisionUseCase:
    def __init__(self, repo: BandejaFormularioRepositoryPort):
        self.repo = repo

    async def execute(self, q: BandejaRevisionQuery) -> List[FormularioInscripcion]:
        return await self.repo.listar_bandeja(q.sede_id, q.gestion, "enviado", q.limit, q.offset)

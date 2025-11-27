# app/application/inscripcion/formularios/listar_historico.py
from typing import List, Optional, Protocol
from pydantic import BaseModel
from app.kernel.domain.inscripcion import FormularioInscripcion

class FormularioQueryRepositoryPort(Protocol):
    async def listar_por_sede_y_gestion(self, sede_id: int, gestion: int, limit: int, offset: int) -> List[FormularioInscripcion]: ...
    async def listar_por_alumno(self, alumno_id: int, limit: int, offset: int) -> List[FormularioInscripcion]: ...

class ListarHistoricoDireccionQuery(BaseModel):
    sede_id: int
    gestion: int
    limit: int = 50
    offset: int = 0

class ListarHistoricoTutorQuery(BaseModel):
    alumno_id: int
    limit: int = 50
    offset: int = 0

class ListarHistoricoDireccionUseCase:
    def __init__(self, repo: FormularioQueryRepositoryPort):
        self.repo = repo

    async def execute(self, q: ListarHistoricoDireccionQuery) -> List[FormularioInscripcion]:
        return await self.repo.listar_por_sede_y_gestion(q.sede_id, q.gestion, q.limit, q.offset)

class ListarHistoricoTutorUseCase:
    def __init__(self, repo: FormularioQueryRepositoryPort):
        self.repo = repo

    async def execute(self, q: ListarHistoricoTutorQuery) -> List[FormularioInscripcion]:
        return await self.repo.listar_por_alumno(q.alumno_id, q.limit, q.offset)

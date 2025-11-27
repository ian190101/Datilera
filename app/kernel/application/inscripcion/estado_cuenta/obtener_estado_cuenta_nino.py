# app/application/inscripcion/estado_cuenta/obtener_estado_cuenta_nino.py
from typing import List, Protocol
from pydantic import BaseModel

class EstadoCuentaNinoRepositoryPort(Protocol):
    async def listar_movimientos(self, alumno_id: int, limit: int = 100) -> List[dict]: ...

class ObtenerEstadoCuentaQuery(BaseModel):
    alumno_id: int
    limit: int = 100

class ObtenerEstadoCuentaNinoUseCase:
    def __init__(self, repo: EstadoCuentaNinoRepositoryPort):
        self.repo = repo

    async def execute(self, q: ObtenerEstadoCuentaQuery) -> List[dict]:
        return await self.repo.listar_movimientos(q.alumno_id, q.limit)

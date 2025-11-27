# app/application/inscripcion/firmas/listar_firmas.py
from typing import List
from pydantic import BaseModel
from app.kernel.domain.inscripcion import Firma
from app.kernel.domain.inscripcion.ports import FirmaRepositoryPort

class ListarFirmasQuery(BaseModel):
    formulario_id: int

class ListarFirmasUseCase:
    def __init__(self, firma_repo: FirmaRepositoryPort):
        self.firma_repo = firma_repo

    async def execute(self, q: ListarFirmasQuery) -> List[Firma]:
        return await self.firma_repo.listar_por_formulario(q.formulario_id)

# app/application/finanzas/arqueo/listar_arqueos.py
"""
CU: Listar arqueos por sede
"""
from dataclasses import dataclass
from typing import List, Optional
from app.kernel.domain.finanzas import ArqueoCaja
from app.kernel.domain.finanzas.ports import ArqueoRepositoryPort


@dataclass
class ListarArqueosQuery:
    sede_id: int
    limite: Optional[int] = 36  


class ListarArqueosUseCase:
    def __init__(self, arqueo_repo: ArqueoRepositoryPort):
        self.arqueo_repo = arqueo_repo

    async def execute(self, query: ListarArqueosQuery) -> List[ArqueoCaja]:
        return await self.arqueo_repo.listar_por_sede(query.sede_id, query.limite)  # ordenados por fecha desc [attached_file:33]

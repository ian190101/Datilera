# app/kernel/application/ia/obtener_consulta.py

from __future__ import annotations

from app.kernel.domain.ia import IAConsulta, ConsultaIANoEncontrada
from app.infrastructure.db.repositories.ia import IAConsultasRepository


class ObtenerConsultaIACU:
    """
    Caso de Uso: Obtener detalle de una consulta IA.
    """

    def __init__(self, repo: IAConsultasRepository):
        self.repo = repo

    async def ejecutar(self, consulta_id: int) -> IAConsulta:
        model = await self.repo.obtener_por_id(consulta_id)
        if model is None:
            raise ConsultaIANoEncontrada(consulta_id)
        return IAConsulta.model_validate(model)

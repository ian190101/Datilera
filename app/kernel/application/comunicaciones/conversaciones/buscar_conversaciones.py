# app/kernel/application/comunicaciones/conversaciones/buscar_conversaciones.py

from typing import List
from app.kernel.domain.comunicaciones import (
    Conversacion,
    ConversacionRepositoryPort,
)


class BuscarConversacionesUseCase:
    """Caso de uso: Buscar conversaciones por asunto."""

    def __init__(self, conversacion_repo: ConversacionRepositoryPort):
        self.conversacion_repo = conversacion_repo

    async def ejecutar(
        self,
        usuario_id: int,
        termino: str,
        limite: int = 20,
    ) -> List[Conversacion]:
        """Busca conversaciones por asunto.
        
        Args:
            usuario_id: Usuario que busca
            termino: Término de búsqueda
            limite: Máximo resultados
            
        Returns:
            Lista de conversaciones encontradas
        """
        termino_limpio = (termino or "").strip()
        if not termino_limpio:
            return []

        return await self.conversacion_repo.buscar_por_asunto(
            usuario_id=usuario_id,
            termino=termino_limpio,
            limite=limite,
        )

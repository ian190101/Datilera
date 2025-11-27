# app/kernel/application/comunicaciones/mensajes/buscar_mensajes.py

from typing import List
from app.kernel.domain.comunicaciones import (
    Mensaje,
    MensajeRepositoryPort,
)


class BuscarMensajesUseCase:
    """Caso de uso: Buscar mensajes por contenido."""

    def __init__(self, mensaje_repo: MensajeRepositoryPort):
        self.mensaje_repo = mensaje_repo

    async def ejecutar(
        self,
        usuario_id: int,
        termino: str,
        limite: int = 20,
    ) -> List[Mensaje]:
        """Busca mensajes por contenido.
        
        Args:
            usuario_id: Usuario que busca
            termino: Término de búsqueda
            limite: Máximo resultados
            
        Returns:
            Lista de mensajes encontrados
        """
        termino_limpio = (termino or "").strip()
        if not termino_limpio:
            return []

        return await self.mensaje_repo.buscar_por_contenido(
            usuario_id=usuario_id,
            termino=termino_limpio,
            limite=limite,
        )

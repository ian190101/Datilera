# app/kernel/application/calendario/tipos_eventos/obtener_tipo_evento.py

from typing import Optional

from app.kernel.domain.calendario import (
    TipoEvento,
    TipoEventoRepositoryPort,
    TipoEventoNoEncontradoError,
)


class ObtenerTipoEventoUseCase:
    """Caso de uso: Obtener tipo de evento por ID."""
    
    def __init__(self, tipo_evento_repo: TipoEventoRepositoryPort):
        self.tipo_evento_repo = tipo_evento_repo
    
    async def ejecutar(self, tipo_id: int) -> TipoEvento:
        """Obtiene un tipo de evento por ID.
        
        Args:
            tipo_id: ID del tipo de evento
            
        Returns:
            TipoEvento encontrado
            
        Raises:
            TipoEventoNoEncontradoError: Si no existe
        """
        tipo = await self.tipo_evento_repo.obtener(tipo_id)
        
        if not tipo:
            raise TipoEventoNoEncontradoError(tipo_id=tipo_id)
        
        return tipo

# app/kernel/application/calendario/tipos_eventos/activar_tipo_evento.py

from app.kernel.domain.calendario import (
    TipoEvento,
    TipoEventoRepositoryPort,
    TipoEventoNoEncontradoError,
)


class ActivarTipoEventoUseCase:
    """Caso de uso: Activar tipo de evento."""
    
    def __init__(self, tipo_evento_repo: TipoEventoRepositoryPort):
        self.tipo_evento_repo = tipo_evento_repo
    
    async def ejecutar(self, tipo_id: int) -> TipoEvento:
        """Activa un tipo de evento.
        
        Args:
            tipo_id: ID del tipo de evento
            
        Returns:
            TipoEvento activado
            
        Raises:
            TipoEventoNoEncontradoError: Si no existe
        """
        return await self.tipo_evento_repo.activar_desactivar(tipo_id, activo=True)

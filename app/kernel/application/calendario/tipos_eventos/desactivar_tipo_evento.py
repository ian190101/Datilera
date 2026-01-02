# app/kernel/application/calendario/tipos_eventos/desactivar_tipo_evento.py

from app.kernel.domain.calendario import (
    TipoEvento,
    TipoEventoRepositoryPort,
    TipoEventoNoEncontradoError,
    TipoEventoEnUsoError,
)


class DesactivarTipoEventoUseCase:
    """Caso de uso: Desactivar tipo de evento.
    
    Reglas:
    - No se puede desactivar si tiene eventos asociados
    """
    
    def __init__(self, tipo_evento_repo: TipoEventoRepositoryPort):
        self.tipo_evento_repo = tipo_evento_repo
    
    async def ejecutar(self, tipo_id: int) -> TipoEvento:
        """Desactiva un tipo de evento.
        
        Args:
            tipo_id: ID del tipo de evento
            
        Returns:
            TipoEvento desactivado
            
        Raises:
            TipoEventoNoEncontradoError: Si no existe
            TipoEventoEnUsoError: Si tiene eventos asociados
        """
        return await self.tipo_evento_repo.activar_desactivar(tipo_id, activo=False)

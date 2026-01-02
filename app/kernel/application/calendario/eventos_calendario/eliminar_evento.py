# app/kernel/application/calendario/eventos/eliminar_evento.py

from app.kernel.domain.calendario import (
    EventoCalendarioRepositoryPort,
    EventoNoEncontradoError,
)


class EliminarEventoUseCase:
    """Caso de uso: Eliminar evento (US-CAL-002).
    
    Reglas:
    - Solo el creador o directora/admin pueden eliminar
    - Elimina también las planificaciones asociadas (cascade)
    """
    
    def __init__(self, evento_repo: EventoCalendarioRepositoryPort):
        self.evento_repo = evento_repo
    
    async def ejecutar(self, evento_id: int) -> bool:
        """Elimina un evento.
        
        Args:
            evento_id: ID del evento a eliminar
            
        Returns:
            True si se eliminó
            
        Raises:
            EventoNoEncontradoError: Si no existe
        """
        eliminado = await self.evento_repo.eliminar(evento_id)
        
        if not eliminado:
            raise EventoNoEncontradoError(evento_id=evento_id)
        
        return True

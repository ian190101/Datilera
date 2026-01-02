# app/kernel/application/calendario/eventos/obtener_evento.py

from app.kernel.domain.calendario import (
    EventoCalendario,
    EventoCalendarioRepositoryPort,
    EventoNoEncontradoError,
)


class ObtenerEventoUseCase:
    """Caso de uso: Obtener evento por ID."""
    
    def __init__(self, evento_repo: EventoCalendarioRepositoryPort):
        self.evento_repo = evento_repo
    
    async def ejecutar(self, evento_id: int) -> EventoCalendario:
        """Obtiene un evento por ID.
        
        Args:
            evento_id: ID del evento
            
        Returns:
            EventoCalendario encontrado
            
        Raises:
            EventoNoEncontradoError: Si no existe
        """
        evento = await self.evento_repo.obtener(evento_id)
        
        if not evento:
            raise EventoNoEncontradoError(evento_id=evento_id)
        
        return evento

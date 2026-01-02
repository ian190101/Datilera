# app/kernel/application/calendario/eventos/rechazar_evento.py

from app.kernel.domain.calendario import (
    EventoCalendarioRepositoryPort,
    EventoNoEncontradoError,
    EventoYaAprobadoError,
)


class RechazarEventoUseCase:
    """Caso de uso: Rechazar evento pendiente (US-CAL-002).
    
    Reglas:
    - Solo directora/admin pueden rechazar
    - Se elimina el evento rechazado
    """
    
    def __init__(self, evento_repo: EventoCalendarioRepositoryPort):
        self.evento_repo = evento_repo
    
    async def ejecutar(self, evento_id: int) -> bool:
        """Rechaza un evento pendiente (lo elimina).
        
        Args:
            evento_id: ID del evento
            
        Returns:
            True si se rechazó/eliminó
            
        Raises:
            EventoNoEncontradoError: Si no existe
            EventoYaAprobadoError: Si ya fue aprobado
        """
        # Obtener evento
        evento = await self.evento_repo.obtener(evento_id)
        if not evento:
            raise EventoNoEncontradoError(evento_id=evento_id)
        
        # Verificar que no esté ya aprobado
        if evento.aprobado:
            raise EventoYaAprobadoError(evento_id=evento_id)
        
        # Eliminar (rechazar)
        return await self.evento_repo.eliminar(evento_id)

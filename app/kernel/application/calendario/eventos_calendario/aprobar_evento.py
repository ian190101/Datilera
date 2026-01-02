# app/kernel/application/calendario/eventos/aprobar_evento.py

from app.kernel.domain.calendario import (
    EventoCalendario,
    EventoCalendarioRepositoryPort,
    EventoNoEncontradoError,
    EventoYaAprobadoError,
)


class AprobarEventoUseCase:
    """Caso de uso: Aprobar evento pendiente (US-CAL-002).
    
    Reglas:
    - Solo directora/admin pueden aprobar
    - El evento debe estar pendiente de aprobación
    """
    
    def __init__(self, evento_repo: EventoCalendarioRepositoryPort):
        self.evento_repo = evento_repo
    
    async def ejecutar(self, evento_id: int, aprobado_por: int) -> EventoCalendario:
        """Aprueba un evento pendiente.
        
        Args:
            evento_id: ID del evento
            aprobado_por: ID del usuario que aprueba
            
        Returns:
            EventoCalendario aprobado
            
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
        
        # Aprobar
        evento.aprobar(aprobado_por)
        
        # Persistir
        return await self.evento_repo.actualizar(evento)

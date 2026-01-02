# app/kernel/application/calendario/eventos/procesar_recordatorios_eventos.py

from datetime import date
from typing import List

from app.kernel.domain.calendario import (
    EventoCalendario,
    EventoCalendarioRepositoryPort,
)


class ProcesarRecordatoriosEventosUseCase:
    """Caso de uso: Procesar recordatorios de eventos (tarea programada).
    
    Reglas:
    - Se ejecuta diariamente
    - Envía notificaciones X días antes del evento
    - Marca recordatorio como enviado
    """
    
    def __init__(self, evento_repo: EventoCalendarioRepositoryPort):
        self.evento_repo = evento_repo
    
    async def ejecutar(self, fecha_actual: date) -> List[EventoCalendario]:
        """Procesa recordatorios de eventos pendientes.
        
        Args:
            fecha_actual: Fecha actual
            
        Returns:
            Lista de eventos que necesitan recordatorio
        """
        # Obtener eventos con recordatorio pendiente
        eventos = await self.evento_repo.obtener_eventos_con_recordatorio_pendiente(fecha_actual)
        
        eventos_procesados = []
        
        for evento in eventos:
            # Marcar como enviado
            evento.marcar_recordatorio_enviado()
            await self.evento_repo.actualizar(evento)
            
            eventos_procesados.append(evento)
        
        return eventos_procesados

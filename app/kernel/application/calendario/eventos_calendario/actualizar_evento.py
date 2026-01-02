# app/kernel/application/calendario/eventos/actualizar_evento.py

from datetime import date, time
from typing import Optional

from app.kernel.domain.calendario import (
    EventoCalendario,
    EventoCalendarioRepositoryPort,
    EventoNoEncontradoError,
    EventoFechaInvalidaError,
    EventoHoraInvalidaError,
)


class ActualizarEventoUseCase:
    """Caso de uso: Actualizar evento (US-CAL-002).
    
    Reglas:
    - Solo el creador o directora/admin pueden actualizar
    - Validar fechas y horarios
    """
    
    def __init__(self, evento_repo: EventoCalendarioRepositoryPort):
        self.evento_repo = evento_repo
    
    async def ejecutar(
        self,
        evento_id: int,
        titulo: Optional[str] = None,
        descripcion: Optional[str] = None,
        fecha: Optional[date] = None,
        fecha_fin: Optional[date] = None,
        todo_el_dia: Optional[bool] = None,
        hora_inicio: Optional[time] = None,
        hora_fin: Optional[time] = None,
        lugar: Optional[str] = None,
        recordatorio_dias_antes: Optional[int] = None,
    ) -> EventoCalendario:
        """Actualiza un evento existente.
        
        Args:
            evento_id: ID del evento
            titulo: Nuevo título (opcional)
            descripcion: Nueva descripción (opcional)
            fecha: Nueva fecha (opcional)
            fecha_fin: Nueva fecha fin (opcional)
            todo_el_dia: Cambiar si es todo el día (opcional)
            hora_inicio: Nueva hora inicio (opcional)
            hora_fin: Nueva hora fin (opcional)
            lugar: Nuevo lugar (opcional)
            recordatorio_dias_antes: Cambiar días recordatorio (opcional)
            
        Returns:
            EventoCalendario actualizado
            
        Raises:
            EventoNoEncontradoError: Si no existe
            EventoFechaInvalidaError: Si las fechas son inválidas
            EventoHoraInvalidaError: Si los horarios son inválidos
        """
        # Obtener evento existente
        evento = await self.evento_repo.obtener(evento_id)
        if not evento:
            raise EventoNoEncontradoError(evento_id=evento_id)
        
        # Actualizar campos
        if titulo is not None:
            evento.titulo = titulo.strip()
        
        if descripcion is not None:
            evento.descripcion = descripcion
        
        if fecha is not None:
            evento.fecha = fecha
        
        if fecha_fin is not None:
            evento.fecha_fin = fecha_fin
        
        # Validar fechas
        if evento.fecha_fin and evento.fecha_fin < evento.fecha:
            raise EventoFechaInvalidaError()
        
        if todo_el_dia is not None:
            evento.todo_el_dia = todo_el_dia
        
        if hora_inicio is not None:
            evento.hora_inicio = hora_inicio
        
        if hora_fin is not None:
            evento.hora_fin = hora_fin
        
        # Validar horarios
        if not evento.todo_el_dia and evento.hora_inicio and evento.hora_fin:
            if evento.hora_fin <= evento.hora_inicio:
                raise EventoHoraInvalidaError()
        
        if lugar is not None:
            evento.lugar = lugar
        
        if recordatorio_dias_antes is not None:
            evento.recordatorio_dias_antes = recordatorio_dias_antes
            evento.recordatorio_enviado = False  # Resetear si se cambia
        
        # Persistir cambios
        return await self.evento_repo.actualizar(evento)

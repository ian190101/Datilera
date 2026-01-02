# app/kernel/application/calendario/eventos/crear_evento.py

from datetime import date, time
from typing import Optional

from app.kernel.domain.calendario import (
    EventoCalendario,
    EventoCalendarioRepositoryPort,
    TipoEventoRepositoryPort,
    TipoEventoNoEncontradoError,
    TipoEventoInactivoError,
    EventoFechaInvalidaError,
    EventoHoraInvalidaError,
    CalendarioCampoRequeridoError,
    CalendarioSedeNoCoincideError,
)


class CrearEventoUseCase:
    """Caso de uso: Crear evento del calendario (US-CAL-002).
    
    Reglas:
    - Título obligatorio
    - Tipo de evento debe existir y estar activo
    - Validar fechas y horarios
    - Si el tipo requiere aprobación, evento queda pendiente
    """
    
    def __init__(
        self,
        evento_repo: EventoCalendarioRepositoryPort,
        tipo_evento_repo: TipoEventoRepositoryPort,
    ):
        self.evento_repo = evento_repo
        self.tipo_evento_repo = tipo_evento_repo
    
    async def ejecutar(
        self,
        titulo: str,
        tipo_evento_id: int,
        fecha: date,
        sede_id: int,
        creado_por: int,
        descripcion: Optional[str] = None,
        fecha_fin: Optional[date] = None,
        todo_el_dia: bool = True,
        hora_inicio: Optional[time] = None,
        hora_fin: Optional[time] = None,
        lugar: Optional[str] = None,
        relacionado_tipo: Optional[str] = None,
        relacionado_id: Optional[int] = None,
        recordatorio_dias_antes: Optional[int] = None,
    ) -> EventoCalendario:
        """Crea un nuevo evento.
        
        Args:
            titulo: Título del evento
            tipo_evento_id: ID del tipo de evento
            fecha: Fecha del evento
            sede_id: ID de la sede
            creado_por: ID del usuario creador
            descripcion: Descripción (opcional)
            fecha_fin: Fecha fin para eventos multi-día (opcional)
            todo_el_dia: Si es todo el día
            hora_inicio: Hora inicio (requerido si no es todo el día)
            hora_fin: Hora fin (requerido si no es todo el día)
            lugar: Ubicación (opcional)
            relacionado_tipo: Tipo de entidad relacionada (opcional)
            relacionado_id: ID de entidad relacionada (opcional)
            recordatorio_dias_antes: Días antes para recordatorio (opcional)
            
        Returns:
            EventoCalendario creado
            
        Raises:
            CalendarioCampoRequeridoError: Si falta campo requerido
            TipoEventoNoEncontradoError: Si el tipo no existe
            TipoEventoInactivoError: Si el tipo está inactivo
            CalendarioSedeNoCoincideError: Si las sedes no coinciden
            EventoFechaInvalidaError: Si las fechas son inválidas
            EventoHoraInvalidaError: Si los horarios son inválidos
        """
        # Validaciones básicas
        if not titulo or not titulo.strip():
            raise CalendarioCampoRequeridoError("titulo")
        
        # Validar tipo de evento
        tipo = await self.tipo_evento_repo.obtener(tipo_evento_id)
        if not tipo:
            raise TipoEventoNoEncontradoError(tipo_id=tipo_evento_id)
        
        if not tipo.activo:
            raise TipoEventoInactivoError(tipo_id=tipo_evento_id)
        
        # Validar que las sedes coincidan
        if tipo.sede_id != sede_id:
            raise CalendarioSedeNoCoincideError(sede_evento=sede_id, sede_tipo=tipo.sede_id)
        
        # Validar fechas
        if fecha_fin and fecha_fin < fecha:
            raise EventoFechaInvalidaError()
        
        # Validar horarios si no es todo el día
        if not todo_el_dia:
            if not hora_inicio or not hora_fin:
                raise CalendarioCampoRequeridoError("hora_inicio y hora_fin son requeridos si no es todo el día")
            
            if hora_fin <= hora_inicio:
                raise EventoHoraInvalidaError()
        
        # Determinar si requiere aprobación
        aprobado = not tipo.requiere_aprobacion
        
        # Crear entidad
        evento = EventoCalendario(
            titulo=titulo.strip(),
            descripcion=descripcion,
            tipo_evento_id=tipo_evento_id,
            fecha=fecha,
            fecha_fin=fecha_fin,
            todo_el_dia=todo_el_dia,
            hora_inicio=hora_inicio,
            hora_fin=hora_fin,
            sede_id=sede_id,
            lugar=lugar,
            relacionado_tipo=relacionado_tipo,
            relacionado_id=relacionado_id,
            aprobado=aprobado,
            recordatorio_dias_antes=recordatorio_dias_antes,
            recordatorio_enviado=False,
            creado_por=creado_por,
        )
        
        # Persistir
        return await self.evento_repo.crear(evento)

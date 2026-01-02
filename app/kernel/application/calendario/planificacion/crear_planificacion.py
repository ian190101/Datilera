# app/kernel/application/calendario/planificacion/crear_planificacion.py

from datetime import date, time
from typing import Optional

from app.kernel.domain.calendario import (
    PlanificacionActividad,
    PlanificacionActividadRepositoryPort,
    EventoCalendarioRepositoryPort,
    EventoNoEncontradoError,
    PlanificacionHoraInvalidaError,
    PlanificacionFechaInvalidaError,
    PlanificacionHorarioConflictoError,
    CalendarioCampoRequeridoError,
)


class CrearPlanificacionUseCase:
    """Caso de uso: Crear planificación de actividad (US-CAL-003).
    
    Reglas:
    - Título obligatorio
    - Fecha no puede ser pasada
    - Hora fin > hora inicio
    - No puede haber conflicto de horarios con otras planificaciones de la misma profesora
    - Opcionalmente puede asociarse a un evento
    """
    
    def __init__(
        self,
        planificacion_repo: PlanificacionActividadRepositoryPort,
        evento_repo: EventoCalendarioRepositoryPort,
    ):
        self.planificacion_repo = planificacion_repo
        self.evento_repo = evento_repo
    
    async def ejecutar(
        self,
        titulo: str,
        fecha: date,
        hora_inicio: time,
        hora_fin: time,
        profesora_id: int,
        sede_id: int,
        descripcion: Optional[str] = None,
        objetivo: Optional[str] = None,
        materiales: Optional[str] = None,
        paralelo_id: Optional[int] = None,
        lugar: Optional[str] = None,
        evento_id: Optional[int] = None,
    ) -> PlanificacionActividad:
        """Crea una nueva planificación de actividad.
        
        Args:
            titulo: Título de la actividad
            fecha: Fecha de la actividad
            hora_inicio: Hora de inicio
            hora_fin: Hora de fin
            profesora_id: ID de la profesora responsable
            sede_id: ID de la sede
            descripcion: Descripción detallada (opcional)
            objetivo: Objetivo pedagógico (opcional)
            materiales: Materiales necesarios (opcional)
            paralelo_id: ID del paralelo (opcional)
            lugar: Ubicación física (opcional)
            evento_id: ID del evento asociado (opcional)
            
        Returns:
            PlanificacionActividad creada
            
        Raises:
            CalendarioCampoRequeridoError: Si falta campo requerido
            PlanificacionFechaInvalidaError: Si la fecha es pasada
            PlanificacionHoraInvalidaError: Si hora_fin <= hora_inicio
            PlanificacionHorarioConflictoError: Si hay conflicto con otra planificación
            EventoNoEncontradoError: Si el evento no existe
        """
        # Validaciones básicas
        if not titulo or not titulo.strip():
            raise CalendarioCampoRequeridoError("titulo")
        
        if not profesora_id:
            raise CalendarioCampoRequeridoError("profesora_id")
        
        # Validar que la fecha no sea pasada (permitir hoy)
        from datetime import date as date_class
        if fecha < date_class.today():
            raise PlanificacionFechaInvalidaError(
                "No se pueden planificar actividades en fechas pasadas"
            )
        
        # Validar horarios
        if hora_fin <= hora_inicio:
            raise PlanificacionHoraInvalidaError()
        
        # Si hay evento asociado, validar que existe
        if evento_id:
            evento = await self.evento_repo.obtener(evento_id)
            if not evento:
                raise EventoNoEncontradoError(evento_id=evento_id)
        
        # Crear entidad
        planificacion = PlanificacionActividad(
            evento_id=evento_id,
            fecha=fecha,
            hora_inicio=hora_inicio,
            hora_fin=hora_fin,
            titulo=titulo.strip(),
            descripcion=descripcion,
            objetivo=objetivo,
            materiales=materiales,
            profesora_id=profesora_id,
            paralelo_id=paralelo_id,
            sede_id=sede_id,
            lugar=lugar,
            completada=False,
        )
        
        # Persistir (el repo valida conflictos de horario)
        return await self.planificacion_repo.crear(planificacion)

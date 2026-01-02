# app/kernel/application/calendario/planificacion/actualizar_planificacion.py

from datetime import date, time
from typing import Optional

from app.kernel.domain.calendario import (
    PlanificacionActividad,
    PlanificacionActividadRepositoryPort,
    PlanificacionNoEncontradaError,
    PlanificacionYaCompletadaError,
    PlanificacionHoraInvalidaError,
    PlanificacionHorarioConflictoError,
)


class ActualizarPlanificacionUseCase:
    """Caso de uso: Actualizar planificación (US-CAL-003).
    
    Reglas:
    - Solo la profesora responsable o directora pueden actualizar
    - No se puede actualizar si ya está completada
    - Validar horarios si se cambian
    """
    
    def __init__(self, planificacion_repo: PlanificacionActividadRepositoryPort):
        self.planificacion_repo = planificacion_repo
    
    async def ejecutar(
        self,
        planificacion_id: int,
        titulo: Optional[str] = None,
        descripcion: Optional[str] = None,
        objetivo: Optional[str] = None,
        materiales: Optional[str] = None,
        fecha: Optional[date] = None,
        hora_inicio: Optional[time] = None,
        hora_fin: Optional[time] = None,
        lugar: Optional[str] = None,
        paralelo_id: Optional[int] = None,
    ) -> PlanificacionActividad:
        """Actualiza una planificación existente.
        
        Args:
            planificacion_id: ID de la planificación
            titulo: Nuevo título (opcional)
            descripcion: Nueva descripción (opcional)
            objetivo: Nuevo objetivo (opcional)
            materiales: Nuevos materiales (opcional)
            fecha: Nueva fecha (opcional)
            hora_inicio: Nueva hora inicio (opcional)
            hora_fin: Nueva hora fin (opcional)
            lugar: Nuevo lugar (opcional)
            paralelo_id: Nuevo paralelo (opcional)
            
        Returns:
            PlanificacionActividad actualizada
            
        Raises:
            PlanificacionNoEncontradaError: Si no existe
            PlanificacionYaCompletadaError: Si ya está completada
            PlanificacionHoraInvalidaError: Si los horarios son inválidos
            PlanificacionHorarioConflictoError: Si hay conflicto
        """
        # Obtener planificación existente
        planificacion = await self.planificacion_repo.obtener(planificacion_id)
        if not planificacion:
            raise PlanificacionNoEncontradaError(planificacion_id=planificacion_id)
        
        # No se puede actualizar si ya está completada
        if planificacion.completada:
            raise PlanificacionYaCompletadaError(planificacion_id=planificacion_id)
        
        # Actualizar campos
        if titulo is not None:
            planificacion.titulo = titulo.strip()
        
        if descripcion is not None:
            planificacion.descripcion = descripcion
        
        if objetivo is not None:
            planificacion.objetivo = objetivo
        
        if materiales is not None:
            planificacion.materiales = materiales
        
        if fecha is not None:
            planificacion.fecha = fecha
        
        if hora_inicio is not None:
            planificacion.hora_inicio = hora_inicio
        
        if hora_fin is not None:
            planificacion.hora_fin = hora_fin
        
        # Validar horarios
        if planificacion.hora_fin <= planificacion.hora_inicio:
            raise PlanificacionHoraInvalidaError()
        
        if lugar is not None:
            planificacion.lugar = lugar
        
        if paralelo_id is not None:
            planificacion.paralelo_id = paralelo_id
        
        # Persistir cambios (el repo valida conflictos)
        return await self.planificacion_repo.actualizar(planificacion)

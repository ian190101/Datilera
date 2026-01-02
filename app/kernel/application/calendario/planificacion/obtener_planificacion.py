# app/kernel/application/calendario/planificacion/obtener_planificacion.py

from app.kernel.domain.calendario import (
    PlanificacionActividad,
    PlanificacionActividadRepositoryPort,
    PlanificacionNoEncontradaError,
)


class ObtenerPlanificacionUseCase:
    """Caso de uso: Obtener planificación por ID."""
    
    def __init__(self, planificacion_repo: PlanificacionActividadRepositoryPort):
        self.planificacion_repo = planificacion_repo
    
    async def ejecutar(self, planificacion_id: int) -> PlanificacionActividad:
        """Obtiene una planificación por ID.
        
        Args:
            planificacion_id: ID de la planificación
            
        Returns:
            PlanificacionActividad encontrada
            
        Raises:
            PlanificacionNoEncontradaError: Si no existe
        """
        planificacion = await self.planificacion_repo.obtener(planificacion_id)
        
        if not planificacion:
            raise PlanificacionNoEncontradaError(planificacion_id=planificacion_id)
        
        return planificacion

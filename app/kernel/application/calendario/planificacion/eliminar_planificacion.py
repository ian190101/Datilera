# app/kernel/application/calendario/planificacion/eliminar_planificacion.py

from app.kernel.domain.calendario import (
    PlanificacionActividadRepositoryPort,
    PlanificacionNoEncontradaError,
    PlanificacionYaCompletadaError,
)


class EliminarPlanificacionUseCase:
    """Caso de uso: Eliminar planificación (US-CAL-003).
    
    Reglas:
    - Solo la profesora responsable o directora pueden eliminar
    - Idealmente no eliminar si ya está completada (mejor mantener historial)
    """
    
    def __init__(self, planificacion_repo: PlanificacionActividadRepositoryPort):
        self.planificacion_repo = planificacion_repo
    
    async def ejecutar(
        self,
        planificacion_id: int,
        permitir_eliminar_completadas: bool = False,
    ) -> bool:
        """Elimina una planificación.
        
        Args:
            planificacion_id: ID de la planificación
            permitir_eliminar_completadas: Si permite eliminar completadas
            
        Returns:
            True si se eliminó
            
        Raises:
            PlanificacionNoEncontradaError: Si no existe
            PlanificacionYaCompletadaError: Si está completada y no se permite eliminar
        """
        # Obtener planificación
        planificacion = await self.planificacion_repo.obtener(planificacion_id)
        if not planificacion:
            raise PlanificacionNoEncontradaError(planificacion_id=planificacion_id)
        
        # Validar si está completada
        if planificacion.completada and not permitir_eliminar_completadas:
            raise PlanificacionYaCompletadaError(planificacion_id=planificacion_id)
        
        # Eliminar
        return await self.planificacion_repo.eliminar(planificacion_id)

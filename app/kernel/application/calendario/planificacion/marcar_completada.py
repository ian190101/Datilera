# app/kernel/application/calendario/planificacion/marcar_completada.py

from typing import Optional

from app.kernel.domain.calendario import (
    PlanificacionActividad,
    PlanificacionActividadRepositoryPort,
    PlanificacionNoEncontradaError,
    PlanificacionYaCompletadaError,
)


class MarcarCompletadaUseCase:
    """Caso de uso: Marcar planificación como completada (US-CAL-003).
    
    Reglas:
    - Solo la profesora responsable puede marcar como completada
    - Se pueden agregar notas de ejecución
    - Una vez completada, no se puede desmarcar (inmutable)
    """
    
    def __init__(self, planificacion_repo: PlanificacionActividadRepositoryPort):
        self.planificacion_repo = planificacion_repo
    
    async def ejecutar(
        self,
        planificacion_id: int,
        notas_ejecucion: Optional[str] = None,
    ) -> PlanificacionActividad:
        """Marca una planificación como completada.
        
        Args:
            planificacion_id: ID de la planificación
            notas_ejecucion: Observaciones post-ejecución (opcional)
            
        Returns:
            PlanificacionActividad marcada como completada
            
        Raises:
            PlanificacionNoEncontradaError: Si no existe
            PlanificacionYaCompletadaError: Si ya está completada
        """
        # Obtener planificación
        planificacion = await self.planificacion_repo.obtener(planificacion_id)
        if not planificacion:
            raise PlanificacionNoEncontradaError(planificacion_id=planificacion_id)
        
        # Validar que no esté ya completada
        if planificacion.completada:
            raise PlanificacionYaCompletadaError(planificacion_id=planificacion_id)
        
        # Marcar como completada
        planificacion.marcar_completada(notas=notas_ejecucion)
        
        # Persistir
        return await self.planificacion_repo.actualizar(planificacion)

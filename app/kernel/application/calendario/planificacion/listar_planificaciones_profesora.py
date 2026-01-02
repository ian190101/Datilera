# app/kernel/application/calendario/planificacion/listar_planificaciones_profesora.py

from datetime import date, timedelta
from typing import List

from app.kernel.domain.calendario import (
    PlanificacionActividad,
    PlanificacionActividadRepositoryPort,
)


class ListarPlanificacionesProfesoraUseCase:
    """Caso de uso: Listar planificaciones de una profesora (US-CAL-003).
    
    Reglas:
    - Vista personalizada para cada profesora
    - Por defecto muestra los próximos 7 días
    """
    
    def __init__(self, planificacion_repo: PlanificacionActividadRepositoryPort):
        self.planificacion_repo = planificacion_repo
    
    async def ejecutar(
        self,
        profesora_id: int,
        dias_adelante: int = 7,
    ) -> List[PlanificacionActividad]:
        """Lista planificaciones de una profesora.
        
        Args:
            profesora_id: ID de la profesora
            dias_adelante: Días hacia adelante desde hoy (default: 7)
            
        Returns:
            Lista de PlanificacionActividad de la profesora
        """
        fecha_inicio = date.today()
        fecha_fin = fecha_inicio + timedelta(days=dias_adelante)
        
        return await self.planificacion_repo.listar_por_rango(
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            profesora_id=profesora_id,
        )

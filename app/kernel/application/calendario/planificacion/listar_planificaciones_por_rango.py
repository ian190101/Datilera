# app/kernel/application/calendario/planificacion/listar_planificaciones_por_rango.py

from datetime import date
from typing import List, Optional

from app.kernel.domain.calendario import (
    PlanificacionActividad,
    PlanificacionActividadRepositoryPort,
)


class ListarPlanificacionesPorRangoUseCase:
    """Caso de uso: Listar planificaciones en un rango de fechas (US-CAL-003).
    
    Reglas:
    - Ordenadas por fecha y hora
    - Útil para vista semanal/mensual
    """
    
    def __init__(self, planificacion_repo: PlanificacionActividadRepositoryPort):
        self.planificacion_repo = planificacion_repo
    
    async def ejecutar(
        self,
        fecha_inicio: date,
        fecha_fin: date,
        sede_id: Optional[int] = None,
        profesora_id: Optional[int] = None,
    ) -> List[PlanificacionActividad]:
        """Lista planificaciones en un rango de fechas.
        
        Args:
            fecha_inicio: Fecha inicial del rango
            fecha_fin: Fecha final del rango
            sede_id: Filtrar por sede (opcional)
            profesora_id: Filtrar por profesora (opcional)
            
        Returns:
            Lista de PlanificacionActividad ordenada por fecha y hora
        """
        return await self.planificacion_repo.listar_por_rango(
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            sede_id=sede_id,
            profesora_id=profesora_id,
        )

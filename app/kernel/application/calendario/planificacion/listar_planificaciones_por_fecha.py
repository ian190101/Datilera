# app/kernel/application/calendario/planificacion/listar_planificaciones_por_fecha.py

from datetime import date
from typing import List, Optional

from app.kernel.domain.calendario import (
    PlanificacionActividad,
    PlanificacionActividadRepositoryPort,
)


class ListarPlanificacionesPorFechaUseCase:
    """Caso de uso: Listar planificaciones de una fecha específica (US-CAL-003).
    
    Reglas:
    - Ordenadas por hora de inicio
    - Filtros opcionales por profesora, paralelo, sede
    """
    
    def __init__(self, planificacion_repo: PlanificacionActividadRepositoryPort):
        self.planificacion_repo = planificacion_repo
    
    async def ejecutar(
        self,
        fecha: date,
        sede_id: Optional[int] = None,
        profesora_id: Optional[int] = None,
        paralelo_id: Optional[int] = None,
    ) -> List[PlanificacionActividad]:
        """Lista planificaciones de una fecha específica.
        
        Args:
            fecha: Fecha a consultar
            sede_id: Filtrar por sede (opcional)
            profesora_id: Filtrar por profesora (opcional)
            paralelo_id: Filtrar por paralelo (opcional)
            
        Returns:
            Lista de PlanificacionActividad ordenada por hora
        """
        return await self.planificacion_repo.listar_por_fecha(
            fecha=fecha,
            sede_id=sede_id,
            profesora_id=profesora_id,
            paralelo_id=paralelo_id,
        )

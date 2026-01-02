# app/kernel/application/calendario/planificacion/obtener_planificaciones_pendientes.py

from datetime import date
from typing import List, Optional

from app.kernel.domain.calendario import (
    PlanificacionActividad,
    PlanificacionActividadRepositoryPort,
)


class ObtenerPlanificacionesPendientesUseCase:
    """Caso de uso: Obtener planificaciones no completadas (US-CAL-003).
    
    Reglas:
    - Útil para recordatorios y seguimiento
    - Muestra planificaciones pasadas y presentes sin completar
    """
    
    def __init__(self, planificacion_repo: PlanificacionActividadRepositoryPort):
        self.planificacion_repo = planificacion_repo
    
    async def ejecutar(
        self,
        fecha_limite: Optional[date] = None,
        sede_id: Optional[int] = None,
        profesora_id: Optional[int] = None,
    ) -> List[PlanificacionActividad]:
        """Obtiene planificaciones pendientes (no completadas).
        
        Args:
            fecha_limite: Fecha límite (default: hoy)
            sede_id: Filtrar por sede (opcional)
            profesora_id: Filtrar por profesora (opcional)
            
        Returns:
            Lista de planificaciones pendientes
        """
        if not fecha_limite:
            fecha_limite = date.today()
        
        # Obtener pendientes del repositorio
        planificaciones = await self.planificacion_repo.obtener_planificaciones_pendientes(
            fecha_limite=fecha_limite,
            sede_id=sede_id,
        )
        
        # Filtrar por profesora si se especifica
        if profesora_id:
            planificaciones = [p for p in planificaciones if p.profesora_id == profesora_id]
        
        return planificaciones

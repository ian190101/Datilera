# app/kernel/application/asistencia/estadisticas/obtener_estadisticas_paralelo.py

from datetime import date
from typing import Dict, Any

from app.kernel.domain.alumnos.ports import AsistenciaAlumnosRepositoryPort


class ObtenerEstadisticasParaleloUseCase:
    """Caso de uso: Obtener estadísticas de asistencia de un paralelo.
    
    Reglas:
    - Calcula presentes, tardanzas, ausentes y justificados
    - Calcula porcentajes de asistencia y retrasos
    - Rango de fechas configurable
    """
    
    def __init__(self, asistencia_repo: AsistenciaAlumnosRepositoryPort):
        self.asistencia_repo = asistencia_repo
    
    async def ejecutar(
        self,
        paralelo_id: int,
        fecha_inicio: date,
        fecha_fin: date
    ) -> Dict[str, Any]:
        """Obtiene estadísticas de asistencia de un paralelo.
        
        Args:
            paralelo_id: ID del paralelo
            fecha_inicio: Fecha inicial del rango
            fecha_fin: Fecha final del rango
            
        Returns:
            Diccionario con estadísticas:
            - paralelo_id
            - fecha_inicio, fecha_fin
            - total_registros
            - total_presentes, total_tarde, total_ausente, total_justificado
            - porcentaje_asistencia, porcentaje_retrasos
        """
        # Obtener estadísticas del repositorio
        estadisticas = await self.asistencia_repo.obtener_estadisticas_paralelo(
            paralelo_id=paralelo_id,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin
        )
        
        return estadisticas

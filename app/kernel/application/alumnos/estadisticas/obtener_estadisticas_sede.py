# app/kernel/application/asistencia/estadisticas/obtener_estadisticas_sede.py

from datetime import date
from typing import Dict, Any

from app.kernel.domain.alumnos.ports import AsistenciaAlumnosRepositoryPort


class ObtenerEstadisticasSedeUseCase:
    """Caso de uso: Obtener estadísticas de asistencia de una sede.
    
    Reglas:
    - Agrupa todas las asistencias de la sede
    - Calcula totales y porcentajes globales
    - Útil para reportes administrativos
    """
    
    def __init__(self, asistencia_repo: AsistenciaAlumnosRepositoryPort):
        self.asistencia_repo = asistencia_repo
    
    async def ejecutar(
        self,
        sede_id: int,
        fecha_inicio: date,
        fecha_fin: date
    ) -> Dict[str, Any]:
        """Obtiene estadísticas de asistencia de una sede.
        
        Args:
            sede_id: ID de la sede
            fecha_inicio: Fecha inicial del rango
            fecha_fin: Fecha final del rango
            
        Returns:
            Diccionario con estadísticas globales de la sede:
            - sede_id
            - fecha_inicio, fecha_fin
            - total_registros
            - total_presentes, total_tarde, total_ausente, total_justificado
            - porcentaje_asistencia, porcentaje_retrasos
        """
        # Obtener estadísticas del repositorio
        estadisticas = await self.asistencia_repo.obtener_estadisticas_sede(
            sede_id=sede_id,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin
        )
        
        return estadisticas

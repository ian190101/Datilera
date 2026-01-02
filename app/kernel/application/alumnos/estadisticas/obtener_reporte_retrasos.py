# app/kernel/application/asistencia/estadisticas/obtener_reporte_retrasos.py

from datetime import date
from typing import List

from app.kernel.domain.alumnos.ports import AsistenciaAlumnosRepositoryPort
from app.kernel.domain.alumnos.asistencia_alumno_entidad import AsistenciaAlumnoEntidad


class ObtenerReporteRetrasosUseCase:
    """Caso de uso: Obtener reporte de retrasos.
    
    Reglas:
    - Lista todos los registros con estado='tarde'
    - Ordenados por fecha descendente
    - Útil para seguimiento y notificaciones a tutores
    """
    
    def __init__(self, asistencia_repo: AsistenciaAlumnosRepositoryPort):
        self.asistencia_repo = asistencia_repo
    
    async def ejecutar(
        self,
        sede_id: int,
        fecha_inicio: date,
        fecha_fin: date,
        limite: int = 100
    ) -> List[AsistenciaAlumnoEntidad]:
        """Obtiene reporte de retrasos.
        
        Args:
            sede_id: ID de la sede
            fecha_inicio: Fecha inicial del rango
            fecha_fin: Fecha final del rango
            limite: Máximo de registros a retornar (default: 100)
            
        Returns:
            Lista de registros de asistencia con retrasos
        """
        # Obtener modelos del repositorio
        modelos = await self.asistencia_repo.obtener_retrasos(
            sede_id=sede_id,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            limite=limite
        )
        
        # Convertir modelos a entidades de dominio
        entidades = [AsistenciaAlumnoEntidad.model_validate(m) for m in modelos]
        
        return entidades

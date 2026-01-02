# app/kernel/application/asistencia/estadisticas/obtener_reporte_faltas.py

from datetime import date
from typing import List

from app.kernel.domain.alumnos.ports import AsistenciaAlumnosRepositoryPort
from app.kernel.domain.alumnos.asistencia_alumno_entidad import AsistenciaAlumnoEntidad


class ObtenerReporteFaltasUseCase:
    """Caso de uso: Obtener reporte de faltas.
    
    Reglas:
    - Lista registros con estado='ausente' o 'justificado'
    - Opción para filtrar solo sin justificar
    - Ordenados por fecha descendente
    - Útil para seguimiento académico y alertas
    """
    
    def __init__(self, asistencia_repo: AsistenciaAlumnosRepositoryPort):
        self.asistencia_repo = asistencia_repo
    
    async def ejecutar(
        self,
        sede_id: int,
        fecha_inicio: date,
        fecha_fin: date,
        solo_sin_justificar: bool = False,
        limite: int = 100
    ) -> List[AsistenciaAlumnoEntidad]:
        """Obtiene reporte de faltas.
        
        Args:
            sede_id: ID de la sede
            fecha_inicio: Fecha inicial del rango
            fecha_fin: Fecha final del rango
            solo_sin_justificar: Si True, solo retorna faltas sin justificar
            limite: Máximo de registros a retornar (default: 100)
            
        Returns:
            Lista de registros de asistencia con faltas
        """
        # Obtener modelos del repositorio
        modelos = await self.asistencia_repo.obtener_faltas(
            sede_id=sede_id,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            solo_sin_justificar=solo_sin_justificar,
            limite=limite
        )
        
        # Convertir modelos a entidades de dominio
        entidades = [AsistenciaAlumnoEntidad.model_validate(m) for m in modelos]
        
        return entidades

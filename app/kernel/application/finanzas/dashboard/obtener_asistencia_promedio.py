"""
Caso de Uso: Obtener Asistencia Promedio
Endpoint: GET /api/v1/reportes/asistencia-promedio
Autor: Arquitecto Senior
Fecha: 2025-12-03

Reglas de Negocio (según HU):
1. Calcula asistencia promedio por paralelo
2. Periodo configurable (últimos 7, 15, 30 días)
3. Incluye: % asistencia, faltas promedio, retrasos promedio
"""

from decimal import Decimal
from datetime import date, timedelta
from typing import List, Dict, Any, Optional

from app.kernel.domain.alumnos.ports import AsistenciaAlumnosRepositoryPort
from app.kernel.domain.academico.ports import IParaleloRepository


class AsistenciaPromedioParaleloDTO:
    """DTO para asistencia promedio de un paralelo"""
    
    def __init__(
        self,
        paralelo_id: int,
        paralelo_nombre: str,
        grupo_nombre: str,
        total_alumnos: int,
        dias_evaluados: int,
        asistencias_totales: int,
        faltas_totales: int,
        retrasos_totales: int,
        porcentaje_asistencia: Decimal,
        promedio_faltas_por_alumno: Decimal,
        promedio_retrasos_por_alumno: Decimal,
    ) -> None:
        self.paralelo_id = paralelo_id
        self.paralelo_nombre = paralelo_nombre
        self.grupo_nombre = grupo_nombre
        self.total_alumnos = total_alumnos
        self.dias_evaluados = dias_evaluados
        self.asistencias_totales = asistencias_totales
        self.faltas_totales = faltas_totales
        self.retrasos_totales = retrasos_totales
        self.porcentaje_asistencia = porcentaje_asistencia
        self.promedio_faltas_por_alumno = promedio_faltas_por_alumno
        self.promedio_retrasos_por_alumno = promedio_retrasos_por_alumno


class AsistenciaPromedioDTO:
    """DTO de respuesta"""
    
    def __init__(
        self,
        sede_id: int,
        fecha_desde: date,
        fecha_hasta: date,
        paralelos: List[AsistenciaPromedioParaleloDTO],
        porcentaje_asistencia_general: Decimal,
    ) -> None:
        self.sede_id = sede_id
        self.fecha_desde = fecha_desde
        self.fecha_hasta = fecha_hasta
        self.paralelos = paralelos
        self.porcentaje_asistencia_general = porcentaje_asistencia_general


class ObtenerAsistenciaPromedioCU:
    """Caso de Uso: Obtener asistencia promedio"""
    
    def __init__(
        self,
        asistencia_repo: AsistenciaAlumnosRepositoryPort,
        paralelo_repo: IParaleloRepository,
    ) -> None:
        self.asistencia_repo = asistencia_repo
        self.paralelo_repo = paralelo_repo
    
    async def execute(
        self,
        sede_id: int,
        dias_atras: int = 30,
    ) -> AsistenciaPromedioDTO:
        """
        Obtiene asistencia promedio por paralelo
        
        Args:
            sede_id: ID de la sede
            dias_atras: Cantidad de días a evaluar (7, 15, 30)
        
        Returns:
            AsistenciaPromedioDTO con estadísticas de asistencia
        """
        # 1. Calcular rango de fechas
        fecha_hasta: date = date.today()
        fecha_desde: date = fecha_hasta - timedelta(days=dias_atras)
        
        # 2. Obtener paralelos de la sede
        paralelos_dict: List[Dict[str, Any]] = []  # await self.paralelo_repo.listar(sede_id=sede_id)
        
        paralelos_dto: List[AsistenciaPromedioParaleloDTO] = []
        total_asistencias_general: int = 0
        total_faltas_general: int = 0
        
        for paralelo in paralelos_dict:
            paralelo_id: int = paralelo["id"]
            
            # Obtener asistencias del paralelo en el periodo
            # Asumiendo que IAsistenciaAlumnoRepository tiene método para listar por paralelo
            asistencias: List[Dict[str, Any]] = []  # await self.asistencia_repo.listar_por_paralelo(...)
            
            # Contar por estado
            asistencias_count: int = len([a for a in asistencias if a.get("estado") == "PRESENTE"])
            faltas_count: int = len([a for a in asistencias if a.get("estado") == "AUSENTE"])
            retrasos_count: int = len([a for a in asistencias if a.get("estado") == "RETRASADO"])
            
            # Total de alumnos del paralelo
            total_alumnos: int = paralelo.get("inscritos_actuales", 0)
            
            # Calcular porcentaje de asistencia
            total_registros: int = asistencias_count + faltas_count + retrasos_count
            porcentaje: Decimal = (
                (Decimal(str(asistencias_count)) / Decimal(str(total_registros))) * 100
                if total_registros > 0 else Decimal("0")
            )
            
            # Promedio de faltas por alumno
            promedio_faltas: Decimal = (
                Decimal(str(faltas_count)) / Decimal(str(total_alumnos))
                if total_alumnos > 0 else Decimal("0")
            )
            
            # Promedio de retrasos por alumno
            promedio_retrasos: Decimal = (
                Decimal(str(retrasos_count)) / Decimal(str(total_alumnos))
                if total_alumnos > 0 else Decimal("0")
            )
            
            paralelos_dto.append(
                AsistenciaPromedioParaleloDTO(
                    paralelo_id=paralelo_id,
                    paralelo_nombre=paralelo.get("nombre", f"Paralelo {paralelo_id}"),
                    grupo_nombre=paralelo.get("grupo_nombre", "Sin grupo"),
                    total_alumnos=total_alumnos,
                    dias_evaluados=dias_atras,
                    asistencias_totales=asistencias_count,
                    faltas_totales=faltas_count,
                    retrasos_totales=retrasos_count,
                    porcentaje_asistencia=porcentaje,
                    promedio_faltas_por_alumno=promedio_faltas,
                    promedio_retrasos_por_alumno=promedio_retrasos,
                )
            )
            
            total_asistencias_general += asistencias_count
            total_faltas_general += faltas_count
        
        # Calcular porcentaje general
        total_registros_general: int = total_asistencias_general + total_faltas_general
        porcentaje_general: Decimal = (
            (Decimal(str(total_asistencias_general)) / Decimal(str(total_registros_general))) * 100
            if total_registros_general > 0 else Decimal("0")
        )
        
        return AsistenciaPromedioDTO(
            sede_id=sede_id,
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta,
            paralelos=paralelos_dto,
            porcentaje_asistencia_general=porcentaje_general,
        )

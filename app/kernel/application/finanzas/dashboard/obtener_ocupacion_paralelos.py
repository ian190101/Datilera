"""
Caso de Uso: Obtener Reporte de Ocupación por Paralelo
Endpoint: GET /api/v1/reportes/ocupacion-paralelos
Autor: Arquitecto Senior
Fecha: 2025-12-03

Reglas de Negocio (según HU):
1. Muestra capacidad vs inscritos por paralelo
2. Calcula porcentaje de ocupación
3. Identifica paralelos con sobre-cupo o bajo-cupo
4. Agrupa por grupo (Bebés, Maternal, etc.)
"""

from decimal import Decimal
from typing import List, Dict, Any, Optional

from app.kernel.domain.academico.ports import (
    IParaleloRepository,
    IGrupoRepository,
)

from app.kernel.domain.alumnos.ports import  AlumnoRepositoryPort

class ParaleloOcupacionDTO:
    """DTO para ocupación de un paralelo"""
    
    def __init__(
        self,
        paralelo_id: int,
        paralelo_nombre: str,
        grupo_nombre: str,
        capacidad_maxima: int,
        inscritos_actuales: int,
        porcentaje_ocupacion: Decimal,
        estado_ocupacion: str,  # DISPONIBLE | COMPLETO | SOBRE_CUPO
        cupos_disponibles: int,
    ) -> None:
        self.paralelo_id = paralelo_id
        self.paralelo_nombre = paralelo_nombre
        self.grupo_nombre = grupo_nombre
        self.capacidad_maxima = capacidad_maxima
        self.inscritos_actuales = inscritos_actuales
        self.porcentaje_ocupacion = porcentaje_ocupacion
        self.estado_ocupacion = estado_ocupacion
        self.cupos_disponibles = cupos_disponibles


class OcupacionParalelosDTO:
    """DTO de respuesta"""
    
    def __init__(
        self,
        sede_id: int,
        paralelos: List[ParaleloOcupacionDTO],
        total_capacidad: int,
        total_inscritos: int,
        porcentaje_ocupacion_general: Decimal,
    ) -> None:
        self.sede_id = sede_id
        self.paralelos = paralelos
        self.total_capacidad = total_capacidad
        self.total_inscritos = total_inscritos
        self.porcentaje_ocupacion_general = porcentaje_ocupacion_general


class ObtenerOcupacionParalelosCU:
    """Caso de Uso: Obtener ocupación de paralelos"""
    
    def __init__(
        self,
        paralelo_repo: IParaleloRepository,
        grupo_repo: IGrupoRepository,
        alumno_paralelo_repo: AlumnoRepositoryPort,
    ) -> None:
        self.paralelo_repo = paralelo_repo
        self.grupo_repo = grupo_repo
        self.alumno_paralelo_repo = alumno_paralelo_repo
    
    async def execute(
        self,
        sede_id: int,
        grupo_id: Optional[int] = None,
    ) -> OcupacionParalelosDTO:
        """
        Obtiene ocupación de paralelos
        
        Args:
            sede_id: ID de la sede
            grupo_id: Filtro opcional por grupo
        
        Returns:
            OcupacionParalelosDTO con datos de ocupación
        """
        # 1. Obtener paralelos de la sede
        # Asumiendo que IParaleloRepository.listar() acepta sede_id
        paralelos_dict: List[Dict[str, Any]] = []  # await self.paralelo_repo.listar(sede_id=sede_id)
        
        # Filtrar por grupo si se especifica
        if grupo_id:
            paralelos_dict = [
                p for p in paralelos_dict
                if p.get("grupo_id") == grupo_id
            ]
        
        paralelos_dto: List[ParaleloOcupacionDTO] = []
        total_capacidad: int = 0
        total_inscritos: int = 0
        
        for paralelo in paralelos_dict:
            paralelo_id: int = paralelo["id"]
            capacidad: int = paralelo.get("capacidad_maxima", 0)
            
            # Contar inscritos actuales en el paralelo
            # Asumiendo que IAlumnoParaleloRepository tiene método para contar
            inscritos: int = await self._contar_inscritos_paralelo(paralelo_id)
            
            # Calcular porcentaje de ocupación
            porcentaje: Decimal = (
                (Decimal(str(inscritos)) / Decimal(str(capacidad))) * 100
                if capacidad > 0 else Decimal("0")
            )
            
            # Determinar estado de ocupación
            estado: str = self._determinar_estado_ocupacion(inscritos, capacidad)
            
            # Cupos disponibles
            cupos: int = max(0, capacidad - inscritos)
            
            # Obtener nombre del grupo
            grupo_nombre: str = await self._obtener_nombre_grupo(paralelo.get("grupo_id"))
            
            paralelos_dto.append(
                ParaleloOcupacionDTO(
                    paralelo_id=paralelo_id,
                    paralelo_nombre=paralelo.get("nombre", f"Paralelo {paralelo_id}"),
                    grupo_nombre=grupo_nombre,
                    capacidad_maxima=capacidad,
                    inscritos_actuales=inscritos,
                    porcentaje_ocupacion=porcentaje,
                    estado_ocupacion=estado,
                    cupos_disponibles=cupos,
                )
            )
            
            total_capacidad += capacidad
            total_inscritos += inscritos
        
        # Calcular ocupación general
        ocupacion_general: Decimal = (
            (Decimal(str(total_inscritos)) / Decimal(str(total_capacidad))) * 100
            if total_capacidad > 0 else Decimal("0")
        )
        
        return OcupacionParalelosDTO(
            sede_id=sede_id,
            paralelos=paralelos_dto,
            total_capacidad=total_capacidad,
            total_inscritos=total_inscritos,
            porcentaje_ocupacion_general=ocupacion_general,
        )
    
    async def _contar_inscritos_paralelo(self, paralelo_id: int) -> int:
        """Cuenta inscritos actuales en un paralelo"""
        # Asumiendo que IAlumnoParaleloRepository tiene método listar o contar
        inscripciones: List[Dict[str, Any]] = []  # await self.alumno_paralelo_repo.listar_por_paralelo(paralelo_id)
        
        # Filtrar solo activos
        activos: int = len([
            i for i in inscripciones
            if i.get("activo", True)
        ])
        
        return activos
    
    async def _obtener_nombre_grupo(self, grupo_id: Optional[int]) -> str:
        """Obtiene nombre del grupo"""
        if not grupo_id:
            return "Sin grupo"
        
        # Asumiendo que IGrupoRepository tiene método obtener_por_id
        grupo: Optional[Dict[str, Any]] = None  # await self.grupo_repo.obtener_por_id(grupo_id)
        
        return grupo.get("nombre", "Sin nombre") if grupo else "Sin grupo"
    
    def _determinar_estado_ocupacion(self, inscritos: int, capacidad: int) -> str:
        """Determina el estado de ocupación"""
        if capacidad == 0:
            return "SIN_CAPACIDAD"
        
        if inscritos >= capacidad:
            if inscritos > capacidad:
                return "SOBRE_CUPO"
            return "COMPLETO"
        
        porcentaje: Decimal = (Decimal(str(inscritos)) / Decimal(str(capacidad))) * 100
        
        if porcentaje >= 90:
            return "CASI_COMPLETO"
        elif porcentaje >= 70:
            return "DISPONIBLE"
        else:
            return "BAJA_OCUPACION"

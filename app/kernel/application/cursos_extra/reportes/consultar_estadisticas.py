# app/kernel/application/cursosextra/reportes/consultar_estadisticas.py

"""
Caso de Uso: Consultar Estadísticas de Curso
"""
from typing import Dict

from app.kernel.domain.cursos_extra import (
    TipoAlumnoCursoExtra,
    CursoExtraRepositoryPort,
    InscripcionCursoExtraRepositoryPort,
    CursoExtraNoEncontrado,
)


class EstadisticasCursoResult:
    """Resultado de estadísticas del curso."""
    def __init__(
        self,
        curso_id: int,
        nombre_curso: str,
        inscritos_totales: int,
        inscritos_internos: int,
        inscritos_externos: int,
        cupo_maximo: int,
        cupos_disponibles: int,
        porcentaje_ocupacion: float,
    ):
        self.curso_id = curso_id
        self.nombre_curso = nombre_curso
        self.inscritos_totales = inscritos_totales
        self.inscritos_internos = inscritos_internos
        self.inscritos_externos = inscritos_externos
        self.cupo_maximo = cupo_maximo
        self.cupos_disponibles = cupos_disponibles
        self.porcentaje_ocupacion = porcentaje_ocupacion


class ConsultarEstadisticas:
    """
    Caso de Uso: Consultar estadísticas de inscripciones de un curso.
    """
    
    def __init__(
        self,
        curso_repo: CursoExtraRepositoryPort,
        inscripcion_repo: InscripcionCursoExtraRepositoryPort,
    ):
        self.curso_repo = curso_repo
        self.inscripcion_repo = inscripcion_repo
    
    async def execute(self, curso_id: int) -> EstadisticasCursoResult:
        """Ejecuta el caso de uso."""
        
        # Obtener curso
        curso = await self.curso_repo.obtener_por_id(curso_id)
        if not curso:
            raise CursoExtraNoEncontrado(curso_id)
        
        # Contar inscritos por tipo
        inscritos_internos = await self.inscripcion_repo.contar_por_tipo(
            curso_id, TipoAlumnoCursoExtra.INTERNO
        )
        inscritos_externos = await self.inscripcion_repo.contar_por_tipo(
            curso_id, TipoAlumnoCursoExtra.EXTERNO
        )
        
        inscritos_totales = inscritos_internos + inscritos_externos
        cupos_disponibles = curso.cupo_maximo - inscritos_totales
        porcentaje_ocupacion = (inscritos_totales / curso.cupo_maximo * 100) if curso.cupo_maximo > 0 else 0
        
        return EstadisticasCursoResult(
            curso_id=curso.id,
            nombre_curso=curso.nombre,
            inscritos_totales=inscritos_totales,
            inscritos_internos=inscritos_internos,
            inscritos_externos=inscritos_externos,
            cupo_maximo=curso.cupo_maximo,
            cupos_disponibles=cupos_disponibles,
            porcentaje_ocupacion=round(porcentaje_ocupacion, 2),
        )

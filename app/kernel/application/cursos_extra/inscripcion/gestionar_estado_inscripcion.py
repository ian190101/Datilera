# app/kernel/application/cursosextra/inscripcion/gestionar_estado_inscripcion.py

"""
Caso de Uso: Gestionar Estado de Inscripción
"""
from app.kernel.domain.cursos_extra import (
    InscripcionCursoExtra,
    EstadoInscripcionCursoExtra,
    InscripcionCursoExtraRepositoryPort,
    CursoExtraRepositoryPort,
    InscripcionNoEncontrada,
    InscripcionYaCompletada,
    InscripcionYaRetirada,
)

from app.kernel.domain.cursos_extra import CuposAgotados

class GestionarEstadoInscripcion:
    """
    Caso de Uso: Cambiar el estado de una inscripción.
    
    Estados posibles:
    - ACTIVO -> COMPLETADO (curso finalizado)
    - ACTIVO -> RETIRADO (alumno se retira)
    - RETIRADO -> ACTIVO (reactivación)
    
    Reglas:
    - Al retirar, se decrementa el contador de inscritos del curso
    - Al reactivar, se incrementa el contador (validando cupos)
    """
    
    def __init__(
        self,
        inscripcion_repo: InscripcionCursoExtraRepositoryPort,
        curso_repo: CursoExtraRepositoryPort,
    ):
        self.inscripcion_repo = inscripcion_repo
        self.curso_repo = curso_repo
    
    async def completar(self, inscripcion_id: int) -> InscripcionCursoExtra:
        """Marca la inscripción como completada."""
        
        inscripcion = await self.inscripcion_repo.obtener_por_id(inscripcion_id)
        if not inscripcion:
            raise InscripcionNoEncontrada(inscripcion_id)
        
        if inscripcion.estado == EstadoInscripcionCursoExtra.COMPLETADO:
            raise InscripcionYaCompletada(inscripcion_id)
        
        return await self.inscripcion_repo.actualizar_estado(
            inscripcion_id, EstadoInscripcionCursoExtra.COMPLETADO
        )
    
    async def retirar(self, inscripcion_id: int) -> InscripcionCursoExtra:
        """Retira al alumno del curso."""
        
        inscripcion = await self.inscripcion_repo.obtener_por_id(inscripcion_id)
        if not inscripcion:
            raise InscripcionNoEncontrada(inscripcion_id)
        
        if inscripcion.estado == EstadoInscripcionCursoExtra.RETIRADO:
            raise InscripcionYaRetirada(inscripcion_id)
        
        # Decrementar contador solo si estaba activo
        if inscripcion.estado == EstadoInscripcionCursoExtra.ACTIVO:
            await self.curso_repo.decrementar_inscritos(inscripcion.curso_extra_id)
        
        return await self.inscripcion_repo.actualizar_estado(
            inscripcion_id, EstadoInscripcionCursoExtra.RETIRADO
        )
    
    async def reactivar(self, inscripcion_id: int) -> InscripcionCursoExtra:
        """Reactiva una inscripción retirada."""
        
        inscripcion = await self.inscripcion_repo.obtener_por_id(inscripcion_id)
        if not inscripcion:
            raise InscripcionNoEncontrada(inscripcion_id)
        
        if inscripcion.estado == EstadoInscripcionCursoExtra.ACTIVO:
            return inscripcion  # Ya está activa
        
        # Validar cupos disponibles
        tiene_cupos = await self.curso_repo.verificar_cupos_disponibles(
            inscripcion.curso_extra_id
        )
        if not tiene_cupos:
            curso = await self.curso_repo.obtener_por_id(inscripcion.curso_extra_id)
            raise CuposAgotados(inscripcion.curso_extra_id, curso.nombre)
        
        # Incrementar contador
        await self.curso_repo.incrementar_inscritos(inscripcion.curso_extra_id)
        
        return await self.inscripcion_repo.actualizar_estado(
            inscripcion_id, EstadoInscripcionCursoExtra.ACTIVO
        )

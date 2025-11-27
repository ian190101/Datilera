# app/kernel/application/cursosextra/inscripcion/obtener_inscripcion.py

"""
Caso de Uso: Obtener Inscripción por ID
"""
from app.kernel.domain.cursos_extra import (
    InscripcionCursoExtra,
    InscripcionCursoExtraRepositoryPort,
    InscripcionNoEncontrada,
)


class ObtenerInscripcion:
    """
    Caso de Uso: Obtener una inscripción por su ID.
    """
    
    def __init__(self, inscripcion_repo: InscripcionCursoExtraRepositoryPort):
        self.inscripcion_repo = inscripcion_repo
    
    async def execute(self, inscripcion_id: int) -> InscripcionCursoExtra:
        """Ejecuta el caso de uso."""
        
        inscripcion = await self.inscripcion_repo.obtener_por_id(inscripcion_id)
        if not inscripcion:
            raise InscripcionNoEncontrada(inscripcion_id)
        
        return inscripcion

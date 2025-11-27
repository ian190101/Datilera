# app/kernel/application/cursosextra/alumno_externo/actualizar_alumno_externo.py

"""
Caso de Uso: Actualizar Alumno Externo
"""
from datetime import date
from typing import Optional

from app.kernel.domain.cursos_extra import (
    AlumnoExterno,
    AlumnoExternoRepositoryPort,
    AlumnoExternoNoEncontrado,
    NombreAlumnoInvalido,
    DatosTutorInvalidos,
)


class ActualizarAlumnoExternoDTO:
    """DTO de entrada para actualizar alumno externo."""
    def __init__(
        self,
        alumno_id: int,
        nombre_completo: Optional[str] = None,
        fecha_nacimiento: Optional[date] = None,
        edad_anios: Optional[int] = None,
        tutor_nombre: Optional[str] = None,
        tutor_celular: Optional[str] = None,
        tutor_email: Optional[str] = None,
    ):
        self.alumno_id = alumno_id
        self.nombre_completo = nombre_completo
        self.fecha_nacimiento = fecha_nacimiento
        self.edad_anios = edad_anios
        self.tutor_nombre = tutor_nombre
        self.tutor_celular = tutor_celular
        self.tutor_email = tutor_email


class ActualizarAlumnoExterno:
    """
    Caso de Uso: Actualizar datos de un alumno externo.
    
    Validaciones:
    - El alumno debe existir
    - Validaciones de formato para campos modificados
    """
    
    def __init__(self, alumno_externo_repo: AlumnoExternoRepositoryPort):
        self.alumno_externo_repo = alumno_externo_repo
    
    async def execute(self, dto: ActualizarAlumnoExternoDTO) -> AlumnoExterno:
        """Ejecuta el caso de uso."""
        
        # Obtener alumno existente
        alumno = await self.alumno_externo_repo.obtener_por_id(dto.alumno_id)
        if not alumno:
            raise AlumnoExternoNoEncontrado(dto.alumno_id)
        
        # Actualizar campos si se proporcionan
        if dto.nombre_completo is not None:
            nombre = dto.nombre_completo.strip()
            if not nombre:
                raise NombreAlumnoInvalido("El nombre no puede estar vacío.")
            if len(nombre) > 200:
                raise NombreAlumnoInvalido("El nombre no puede superar 200 caracteres.")
            alumno.nombre_completo = nombre
        
        if dto.fecha_nacimiento is not None:
            alumno.fecha_nacimiento = dto.fecha_nacimiento
        
        if dto.edad_anios is not None:
            alumno.edad_anios = dto.edad_anios
        
        if dto.tutor_nombre is not None:
            tutor_nombre = dto.tutor_nombre.strip()
            if not tutor_nombre:
                raise DatosTutorInvalidos("El nombre del tutor no puede estar vacío.")
            if len(tutor_nombre) > 200:
                raise DatosTutorInvalidos("El nombre del tutor no puede superar 200 caracteres.")
            alumno.tutor_nombre = tutor_nombre
        
        if dto.tutor_celular is not None:
            tutor_celular = dto.tutor_celular.strip()
            if not tutor_celular:
                raise DatosTutorInvalidos("El celular del tutor no puede estar vacío.")
            if len(tutor_celular) > 15:
                raise DatosTutorInvalidos("El celular no puede superar 15 caracteres.")
            alumno.tutor_celular = tutor_celular
        
        if dto.tutor_email is not None:
            alumno.tutor_email = dto.tutor_email
        
        # Persistir cambios
        return await self.alumno_externo_repo.guardar(alumno)

# app/kernel/application/cursosextra/alumno_externo/registrar_alumno_externo.py

"""
Caso de Uso: Registrar Alumno Externo
"""
from datetime import date
from typing import Optional

from app.kernel.domain.cursos_extra import (
    AlumnoExterno,
    AlumnoExternoRepositoryPort,
    AlumnoExternoDuplicado,
    NombreAlumnoInvalido,
    DatosTutorInvalidos,
)


class RegistrarAlumnoExternoDTO:
    """DTO de entrada para registrar alumno externo."""
    def __init__(
        self,
        sede_id: int,
        nombre_completo: str,
        tutor_nombre: str,
        tutor_celular: str,
        fecha_nacimiento: Optional[date] = None,
        edad_anios: Optional[int] = None,
        tutor_email: Optional[str] = None,
        registrado_por_id: Optional[int] = None,
    ):
        self.sede_id = sede_id
        self.nombre_completo = nombre_completo
        self.fecha_nacimiento = fecha_nacimiento
        self.edad_anios = edad_anios
        self.tutor_nombre = tutor_nombre
        self.tutor_celular = tutor_celular
        self.tutor_email = tutor_email
        self.registrado_por_id = registrado_por_id


class RegistrarAlumnoExterno:
    """
    Caso de Uso: Registrar un alumno externo en el sistema.
    
    Validaciones:
    - Nombre completo obligatorio y válido
    - Datos del tutor completos (nombre y celular)
    - No debe existir un alumno externo con el mismo nombre y tutor en la sede
    """
    
    def __init__(self, alumno_externo_repo: AlumnoExternoRepositoryPort):
        self.alumno_externo_repo = alumno_externo_repo
    
    async def execute(self, dto: RegistrarAlumnoExternoDTO) -> AlumnoExterno:
        """Ejecuta el caso de uso."""
        
        # Validación de nombre
        nombre = (dto.nombre_completo or "").strip()
        if not nombre:
            raise NombreAlumnoInvalido("El nombre completo del niño es obligatorio.")
        if len(nombre) > 200:
            raise NombreAlumnoInvalido("El nombre no puede superar 200 caracteres.")
        
        # Validación de datos del tutor
        tutor_nombre = (dto.tutor_nombre or "").strip()
        if not tutor_nombre:
            raise DatosTutorInvalidos("El nombre del tutor es obligatorio.")
        if len(tutor_nombre) > 200:
            raise DatosTutorInvalidos("El nombre del tutor no puede superar 200 caracteres.")
        
        tutor_celular = (dto.tutor_celular or "").strip()
        if not tutor_celular:
            raise DatosTutorInvalidos("El celular del tutor es obligatorio.")
        if len(tutor_celular) > 15:
            raise DatosTutorInvalidos("El celular no puede superar 15 caracteres.")
        
        # Validación de duplicados
        existe = await self.alumno_externo_repo.existe_por_nombre_y_tutor(
            nombre_completo=nombre,
            tutor_celular=tutor_celular,
            sede_id=dto.sede_id
        )
        if existe:
            raise AlumnoExternoDuplicado(nombre, tutor_celular, dto.sede_id)
        
        # Crear entidad
        alumno = AlumnoExterno(
            id=0,
            sede_id=dto.sede_id,
            nombre_completo=nombre,
            fecha_nacimiento=dto.fecha_nacimiento,
            edad_anios=dto.edad_anios,
            tutor_nombre=tutor_nombre,
            tutor_celular=tutor_celular,
            tutor_email=dto.tutor_email,
        )
        
        return await self.alumno_externo_repo.crear(alumno)

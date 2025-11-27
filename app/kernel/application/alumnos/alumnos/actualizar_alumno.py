# app/application/alumnos/alumnos/actualizar_alumno_cu.py

from typing import Optional
from datetime import date, datetime

from app.kernel.domain.alumnos.alumno_entidad import AlumnoEntidad
from app.kernel.domain.alumnos.ports import AlumnoRepositoryPort
from app.kernel.domain.alumnos.errors import (
    AlumnoNoEncontradoError,
    AlumnoDuplicadoError
)


class ActualizarAlumnoCU:
    """Caso de uso: Actualizar datos de un alumno"""

    def __init__(self, alumno_repo: AlumnoRepositoryPort):
        self.alumno_repo = alumno_repo

    async def ejecutar(
        self,
        alumno_id: int,
        nombres: Optional[str] = None,
        apellido_paterno: Optional[str] = None,
        apellido_materno: Optional[str] = None,
        fecha_nacimiento: Optional[date] = None,
        genero: Optional[str] = None,
        numero_documento: Optional[str] = None,
        tipo_documento: Optional[str] = None,
        turno_id: Optional[int] = None,
        foto_url: Optional[str] = None,
        estado: Optional[str] = None,
        activo: Optional[bool] = None
    ) -> AlumnoEntidad:
        """
        Actualizar datos del alumno
        
        Args:
            alumno_id: ID del alumno a actualizar
            (resto de campos opcionales)
            
        Returns:
            AlumnoEntidad: Alumno actualizado
            
        Raises:
            AlumnoNoEncontradoError: Si el alumno no existe
            AlumnoDuplicadoError: Si el nuevo documento ya existe
        """
        
        # Verificar que existe
        alumno = await self.alumno_repo.obtener_por_id(alumno_id)
        if not alumno:
            raise AlumnoNoEncontradoError(alumno_id=alumno_id)
        
        # Si cambia el documento, verificar que no exista otro alumno con ese documento
        if numero_documento and numero_documento != alumno.numero_documento:
            existente = await self.alumno_repo.obtener_por_documento(numero_documento)
            if existente and existente.id != alumno_id:
                raise AlumnoDuplicadoError("numero_documento", numero_documento)
        
        # Actualizar campos proporcionados
        datos_actualizar = {}
        
        if nombres is not None:
            datos_actualizar['nombres'] = nombres.strip()
        if apellido_paterno is not None:
            datos_actualizar['apellido_paterno'] = apellido_paterno.strip()
        if apellido_materno is not None:
            datos_actualizar['apellido_materno'] = apellido_materno.strip() if apellido_materno else None
        if fecha_nacimiento is not None:
            datos_actualizar['fecha_nacimiento'] = fecha_nacimiento
        if genero is not None:
            datos_actualizar['genero'] = genero.upper()
        if numero_documento is not None:
            datos_actualizar['numero_documento'] = numero_documento.strip()
        if tipo_documento is not None:
            datos_actualizar['tipo_documento'] = tipo_documento
        if turno_id is not None:
            datos_actualizar['turno_id'] = turno_id
        if foto_url is not None:
            datos_actualizar['foto_url'] = foto_url
        if estado is not None:
            datos_actualizar['estado'] = estado
        if activo is not None:
            datos_actualizar['activo'] = activo
        
        datos_actualizar['actualizado_en'] = datetime.utcnow()
        
        # Crear entidad actualizada
        alumno_actualizado = AlumnoEntidad(**{**alumno.model_dump(), **datos_actualizar})
        
        # Persistir
        return await self.alumno_repo.actualizar(alumno_id, alumno_actualizado)

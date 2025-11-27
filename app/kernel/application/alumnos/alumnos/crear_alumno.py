# app/application/alumnos/alumnos/crear_alumno.py

from typing import Optional
from datetime import date, datetime

from app.kernel.domain.alumnos.alumno_entidad import AlumnoEntidad
from app.kernel.domain.alumnos.ports import AlumnoRepositoryPort
from app.kernel.domain.alumnos.errors import (
    AlumnoDuplicadoError,
    AlumnoMenorEdadError,
    DatosInvalidosError
)


class CrearAlumnoCU:
    """Caso de uso: Crear un nuevo alumno en el sistema"""

    def __init__(self, alumno_repo: AlumnoRepositoryPort):
        self.alumno_repo = alumno_repo

    async def ejecutar(
        self,
        sede_id: int,
        nombres: str,
        apellido_paterno: str,
        fecha_nacimiento: date,
        genero: str,
        numero_documento: str,
        turno_id: int,
        apellido_materno: Optional[str] = None,
        tipo_documento: str = "CI",
        fecha_ingreso: Optional[date] = None,
        creado_por_id: Optional[int] = None
    ) -> AlumnoEntidad:
        """
        Crear un nuevo alumno con validaciones de negocio
        
        Args:
            sede_id: ID de la sede
            nombres: Nombres del alumno
            apellido_paterno: Apellido paterno
            fecha_nacimiento: Fecha de nacimiento
            genero: Género (M/F)
            numero_documento: Número de documento de identidad
            turno_id: ID del turno asignado
            apellido_materno: Apellido materno (opcional)
            tipo_documento: Tipo de documento (CI por defecto)
            fecha_ingreso: Fecha de ingreso (hoy por defecto)
            creado_por_id: ID del usuario que crea el registro
            
        Returns:
            AlumnoEntidad: Alumno creado
            
        Raises:
            AlumnoDuplicadoError: Si ya existe un alumno con ese documento
            AlumnoMenorEdadError: Si no cumple la edad mínima
            DatosInvalidosError: Si los datos son inválidos
        """
        
        # Validar que no exista alumno con el mismo documento
        alumno_existente = await self.alumno_repo.obtener_por_documento(numero_documento)
        if alumno_existente:
            raise AlumnoDuplicadoError("numero_documento", numero_documento)
        
        # Validar edad mínima (6 meses = 0.5 años)
        edad = self._calcular_edad(fecha_nacimiento)
        if edad < 0.5:
            raise AlumnoMenorEdadError(edad, 0.5)
        
        # Generar código único de alumno
        codigo_alumno = await self._generar_codigo_alumno(sede_id)
        
        # Crear entidad de alumno
        alumno = AlumnoEntidad(
            sede_id=sede_id,
            codigo_alumno=codigo_alumno,
            nombres=nombres.strip(),
            apellido_paterno=apellido_paterno.strip(),
            apellido_materno=apellido_materno.strip() if apellido_materno else None,
            fecha_nacimiento=fecha_nacimiento,
            genero=genero.upper(),
            tipo_documento=tipo_documento,
            numero_documento=numero_documento.strip(),
            turno_id=turno_id,
            fecha_ingreso=fecha_ingreso or date.today(),
            estado="activo",
            activo=True,
            creado_en=datetime.utcnow(),
            creado_por_id=creado_por_id
        )
        
        # Persistir alumno
        return await self.alumno_repo.crear(alumno)
    
    def _calcular_edad(self, fecha_nacimiento: date) -> float:
        """Calcula la edad en años (con decimales)"""
        hoy = date.today()
        edad = hoy.year - fecha_nacimiento.year
        if (hoy.month, hoy.day) < (fecha_nacimiento.month, fecha_nacimiento.day):
            edad -= 1
        # Agregar fracción de año
        dias_transcurridos = (hoy - fecha_nacimiento).days
        return dias_transcurridos / 365.25
    
    async def _generar_codigo_alumno(self, sede_id: int) -> str:
        """Genera código único para el alumno"""
        # Formato: SEDE-AÑO-SECUENCIAL
        # Ejemplo: S01-2025-001
        año = datetime.now().year
        
        # Obtener todos los alumnos de la sede del año actual
        alumnos_sede = await self.alumno_repo.listar_por_sede(sede_id, solo_activos=False)
        alumnos_año = [
            a for a in alumnos_sede 
            if a.codigo_alumno and str(año) in a.codigo_alumno
        ]
        
        secuencial = len(alumnos_año) + 1
        return f"S{sede_id:02d}-{año}-{secuencial:03d}"

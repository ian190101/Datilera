# app/domain/ports/alumnos/ports.py

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from datetime import date

from app.kernel.domain.alumnos.alumno_entidad import AlumnoEntidad
from app.kernel.domain.alumnos.tutor_entidad import TutorEntidad
from app.kernel.domain.alumnos.alumno_tutor_entidad import AlumnoTutorEntidad
from app.kernel.domain.alumnos.alumno_hermano_entidad import AlumnoHermanoEntidad
from app.kernel.domain.alumnos.autorizacion_retiro_entidad import AutorizacionRetiroEntidad
from app.kernel.domain.alumnos.asistencia_alumno_entidad import AsistenciaAlumnoEntidad
from app.kernel.domain.alumnos.asistencia_personal_entidad import AsistenciaPersonalEntidad
from app.kernel.domain.alumnos.permiso_personal_entidad import PermisoPersonalEntidad
from app.kernel.domain.alumnos.consentimiento_entidad import ConsentimientoEntidad
from app.kernel.domain.alumnos.alumno_paralelo_entidad import AlumnoParaleloEntidad


# ============================================================================
# ALUMNOS
# ============================================================================

class AlumnoRepositoryPort(ABC):
    """Puerto para el repositorio de alumnos"""

    @abstractmethod
    async def crear(self, alumno: AlumnoEntidad) -> AlumnoEntidad:
        """Crear un nuevo alumno"""
        pass

    @abstractmethod
    async def obtener_por_id(self, id: int) -> Optional[AlumnoEntidad]:
        """Obtener alumno por ID"""
        pass

    @abstractmethod
    async def obtener_por_codigo(self, codigo: str) -> Optional[AlumnoEntidad]:
        """Obtener alumno por código único"""
        pass

    @abstractmethod
    async def obtener_por_documento(self, numero_documento: str) -> Optional[AlumnoEntidad]:
        """Obtener alumno por número de documento"""
        pass

    @abstractmethod
    async def listar_por_sede(self, sede_id: int, solo_activos: bool = True) -> List[AlumnoEntidad]:
        """Listar alumnos de una sede"""
        pass

    @abstractmethod
    async def listar_por_turno(self, turno_id: int, solo_activos: bool = True) -> List[AlumnoEntidad]:
        """Listar alumnos de un turno"""
        pass

    @abstractmethod
    async def buscar(self, termino: str, sede_id: Optional[int] = None) -> List[AlumnoEntidad]:
        """Buscar alumnos por nombre o documento"""
        pass

    @abstractmethod
    async def actualizar(self, id: int, alumno: AlumnoEntidad) -> AlumnoEntidad:
        """Actualizar alumno"""
        pass

    @abstractmethod
    async def eliminar(self, id: int) -> bool:
        """Eliminar alumno (soft delete)"""
        pass


# ============================================================================
# TUTORES
# ============================================================================

class TutorRepositoryPort(ABC):
    """Puerto para el repositorio de tutores"""

    @abstractmethod
    async def crear(self, tutor: TutorEntidad) -> TutorEntidad:
        """Crear un nuevo tutor"""
        pass

    @abstractmethod
    async def obtener_por_id(self, id: int) -> Optional[TutorEntidad]:
        """Obtener tutor por ID"""
        pass

    @abstractmethod
    async def obtener_por_documento(self, numero_documento: str) -> Optional[TutorEntidad]:
        """Obtener tutor por número de documento"""
        pass

    @abstractmethod
    async def buscar(self, termino: str) -> List[TutorEntidad]:
        """Buscar tutores por nombre o documento"""
        pass

    @abstractmethod
    async def actualizar(self, id: int, tutor: TutorEntidad) -> TutorEntidad:
        """Actualizar tutor"""
        pass

    @abstractmethod
    async def eliminar(self, id: int) -> bool:
        """Eliminar tutor"""
        pass


# ============================================================================
# RELACIÓN ALUMNO-TUTOR
# ============================================================================

class AlumnoTutorRepositoryPort(ABC):
    """Puerto para el repositorio de relación alumno-tutor"""

    @abstractmethod
    async def crear(self, relacion: AlumnoTutorEntidad) -> AlumnoTutorEntidad:
        """Crear relación alumno-tutor"""
        pass

    @abstractmethod
    async def obtener_por_id(self, id: int) -> Optional[AlumnoTutorEntidad]:
        """Obtener relación por ID"""
        pass

    @abstractmethod
    async def listar_por_alumno(self, alumno_id: int) -> List[AlumnoTutorEntidad]:
        """Listar tutores de un alumno"""
        pass

    @abstractmethod
    async def listar_por_tutor(self, tutor_id: int) -> List[AlumnoTutorEntidad]:
        """Listar alumnos de un tutor"""
        pass

    @abstractmethod
    async def obtener_tutor_principal(self, alumno_id: int) -> Optional[AlumnoTutorEntidad]:
        """Obtener el tutor principal de un alumno"""
        pass

    @abstractmethod
    async def actualizar(self, id: int, relacion: AlumnoTutorEntidad) -> AlumnoTutorEntidad:
        """Actualizar relación"""
        pass

    @abstractmethod
    async def eliminar(self, id: int) -> bool:
        """Eliminar relación"""
        pass


# ============================================================================
# HERMANOS
# ============================================================================

class AlumnosHermanosRepositoryPort(ABC):
    """Puerto para el repositorio de hermanos"""

    @abstractmethod
    async def crear(self, hermano: AlumnoHermanoEntidad) -> AlumnoHermanoEntidad:
        """Crear registro de hermano"""
        pass

    @abstractmethod
    async def obtener_por_id(self, id: int) -> Optional[AlumnoHermanoEntidad]:
        """Obtener hermano por ID"""
        pass

    @abstractmethod
    async def listar_por_alumno(self, alumno_id: int) -> List[AlumnoHermanoEntidad]:
        """Listar hermanos de un alumno"""
        pass

    @abstractmethod
    async def actualizar(self, id: int, hermano: AlumnoHermanoEntidad) -> AlumnoHermanoEntidad:
        """Actualizar datos de hermano"""
        pass

    @abstractmethod
    async def eliminar(self, id: int) -> bool:
        """Eliminar registro de hermano"""
        pass


# ============================================================================
# AUTORIZACIONES DE RETIRO
# ============================================================================

class AutorizacionesRetiroRepositoryPort(ABC):
    """Puerto para el repositorio de autorizaciones de retiro"""

    @abstractmethod
    async def crear(self, autorizacion: AutorizacionRetiroEntidad) -> AutorizacionRetiroEntidad:
        """Crear autorización de retiro"""
        pass

    @abstractmethod
    async def obtener_por_id(self, id: int) -> Optional[AutorizacionRetiroEntidad]:
        """Obtener autorización por ID"""
        pass

    @abstractmethod
    async def listar_por_alumno(self, alumno_id: int, solo_activas: bool = True) -> List[AutorizacionRetiroEntidad]:
        """Listar autorizaciones de un alumno"""
        pass

    @abstractmethod
    async def obtener_por_ci(self, alumno_id: int, ci_numero: str) -> Optional[AutorizacionRetiroEntidad]:
        """Buscar autorización activa por CI"""
        pass

    @abstractmethod
    async def desactivar(self, id: int) -> AutorizacionRetiroEntidad:
        """Desactivar una autorización"""
        pass

    @abstractmethod
    async def eliminar(self, id: int) -> bool:
        """Eliminar autorización"""
        pass


# ============================================================================
# ASISTENCIA DE ALUMNOS
# ============================================================================

class AsistenciaAlumnosRepositoryPort(ABC):
    """Puerto para el repositorio de asistencia de alumnos"""

    @abstractmethod
    async def crear(self, asistencia: AsistenciaAlumnoEntidad) -> AsistenciaAlumnoEntidad:
        """Registrar asistencia de alumno"""
        pass

    @abstractmethod
    async def obtener_por_id(self, id: int) -> Optional[AsistenciaAlumnoEntidad]:
        """Obtener registro de asistencia por ID"""
        pass

    @abstractmethod
    async def obtener_por_alumno_fecha(self, alumno_id: int, fecha: date) -> Optional[AsistenciaAlumnoEntidad]:
        """Obtener asistencia de un alumno en fecha específica"""
        pass

    @abstractmethod
    async def listar_por_alumno(
        self, 
        alumno_id: int, 
        fecha_desde: Optional[date] = None, 
        fecha_hasta: Optional[date] = None
    ) -> List[AsistenciaAlumnoEntidad]:
        """Listar asistencias de un alumno en rango de fechas"""
        pass

    @abstractmethod
    async def listar_por_sede_fecha(self, sede_id: int, fecha: date) -> List[AsistenciaAlumnoEntidad]:
        """Listar todas las asistencias de una sede en una fecha"""
        pass

    @abstractmethod
    async def actualizar(self, id: int, asistencia: AsistenciaAlumnoEntidad) -> AsistenciaAlumnoEntidad:
        """Actualizar registro de asistencia"""
        pass
    # app/kernel/domain/asistencia/ports/asistencia_alumnos_repository_port.py

    @abstractmethod
    async def obtener_estadisticas_paralelo(
        self,
        paralelo_id: int,
        fecha_inicio: date,
        fecha_fin: date
    ) -> Dict[str, Any]:
        """Obtiene estadísticas de asistencia de un paralelo."""
        pass

    @abstractmethod
    async def obtener_estadisticas_sede(
        self,
        sede_id: int,
        fecha_inicio: date,
        fecha_fin: date
    ) -> Dict[str, Any]:
        """Obtiene estadísticas de asistencia de una sede."""
        pass

    @abstractmethod
    async def obtener_retrasos(
        self,
        sede_id: int,
        fecha_inicio: date,
        fecha_fin: date,
        limite: int = 100
    ) -> List[AsistenciaAlumnoEntidad]:
        """Obtiene registros de retrasos."""
        pass

    @abstractmethod
    async def obtener_faltas(
        self,
        sede_id: int,
        fecha_inicio: date,
        fecha_fin: date,
        solo_sin_justificar: bool = False,
        limite: int = 100
    ) -> List[AsistenciaAlumnoEntidad]:
        """Obtiene registros de faltas."""
        pass



# ============================================================================
# ASISTENCIA DE PERSONAL
# ============================================================================

class AsistenciaPersonalRepositoryPort(ABC):
    """Puerto para el repositorio de asistencia del personal"""

    @abstractmethod
    async def crear(self, asistencia: AsistenciaPersonalEntidad) -> AsistenciaPersonalEntidad:
        """Registrar entrada/salida de personal"""
        pass

    @abstractmethod
    async def obtener_por_id(self, id: int) -> Optional[AsistenciaPersonalEntidad]:
        """Obtener registro por ID"""
        pass

    @abstractmethod
    async def obtener_por_personal_fecha(self, personal_id: int, fecha: date) -> Optional[AsistenciaPersonalEntidad]:
        """Obtener asistencia de personal en fecha específica"""
        pass

    @abstractmethod
    async def listar_por_sede_fecha(self, sede_id: int, fecha: date) -> List[AsistenciaPersonalEntidad]:
        """Listar asistencias de personal de una sede en una fecha"""
        pass

    @abstractmethod
    async def actualizar(self, id: int, asistencia: AsistenciaPersonalEntidad) -> AsistenciaPersonalEntidad:
        """Actualizar registro (ej: hora de salida)"""
        pass


# ============================================================================
# PERMISOS DE PERSONAL
# ============================================================================

class PermisosPersonalRepositoryPort(ABC):
    """Puerto para el repositorio de permisos del personal"""

    @abstractmethod
    async def crear(self, permiso: PermisoPersonalEntidad) -> PermisoPersonalEntidad:
        """Crear solicitud de permiso"""
        pass

    @abstractmethod
    async def obtener_por_id(self, id: int) -> Optional[PermisoPersonalEntidad]:
        """Obtener permiso por ID"""
        pass

    @abstractmethod
    async def listar_por_sede(self, sede_id: int, estado: Optional[str] = None) -> List[PermisoPersonalEntidad]:
        """Listar permisos de una sede, opcionalmente filtrados por estado"""
        pass

    @abstractmethod
    async def listar_por_personal(self, personal_id: int) -> List[PermisoPersonalEntidad]:
        """Listar permisos de un personal"""
        pass

    @abstractmethod
    async def actualizar_estado(
        self, 
        id: int, 
        estado: str, 
        aprobado_por_id: int
    ) -> PermisoPersonalEntidad:
        """Aprobar o rechazar permiso"""
        pass


# ============================================================================
# CONSENTIMIENTOS
# ============================================================================

class ConsentimientosRepositoryPort(ABC):
    """Puerto para el repositorio de consentimientos"""

    @abstractmethod
    async def crear(self, consentimiento: ConsentimientoEntidad) -> ConsentimientoEntidad:
        """Crear consentimiento para alumno"""
        pass

    @abstractmethod
    async def obtener_por_alumno(self, alumno_id: int) -> Optional[ConsentimientoEntidad]:
        """Obtener consentimiento de un alumno"""
        pass

    @abstractmethod
    async def actualizar(self, alumno_id: int, consentimiento: ConsentimientoEntidad) -> ConsentimientoEntidad:
        """Actualizar consentimientos"""
        pass


# ============================================================================
# ALUMNOS-PARALELOS
# ============================================================================

class AlumnosParalelosRepositoryPort(ABC):
    """Puerto para el repositorio de asignación alumno-paralelo"""

    @abstractmethod
    async def crear(self, asignacion: AlumnoParaleloEntidad) -> AlumnoParaleloEntidad:
        """Asignar alumno a paralelo"""
        pass

    @abstractmethod
    async def obtener_por_id(self, id: int) -> Optional[AlumnoParaleloEntidad]:
        """Obtener asignación por ID"""
        pass

    @abstractmethod
    async def listar_por_alumno(self, alumno_id: int) -> List[AlumnoParaleloEntidad]:
        """Listar paralelos de un alumno"""
        pass

    @abstractmethod
    async def listar_por_paralelo(self, paralelo_id: int) -> List[AlumnoParaleloEntidad]:
        """Listar alumnos de un paralelo"""
        pass

    @abstractmethod
    async def actualizar(self, id: int, asignacion: AlumnoParaleloEntidad) -> AlumnoParaleloEntidad:
        """Actualizar asignación"""
        pass

    @abstractmethod
    async def eliminar(self, id: int) -> bool:
        """Eliminar asignación"""
        pass

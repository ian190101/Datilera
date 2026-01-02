# app/application/alumnos/__init__.py

# Alumnos
from .alumnos import (
    CrearAlumnoCU,
    ObtenerAlumnoCU,
    ActualizarAlumnoCU,
    ListarAlumnosCU,
    BuscarAlumnosCU,
    EliminarAlumnoCU,
)

# Tutores
from .tutor import (
    CrearTutorCU,
    ObtenerTutorCU,
    ActualizarTutorCU,
    BuscarTutoresCU,
    EliminarTutorCU,
    AsignarTutorAlumnoCU,
    ListarTutoresAlumnoCU,
    ActualizarRelacionTutorCU,
    EliminarRelacionTutorCU,
)

from .estadisticas import (
    ObtenerEstadisticasParaleloUseCase,
    ObtenerEstadisticasSedeUseCase,
    ObtenerReporteFaltasUseCase,
    ObtenerReporteRetrasosUseCase,
)


# Hermanos
from .hermanos import (
    RegistrarHermanoCU,
    ListarHermanosCU,
    ActualizarHermanoCU,
    EliminarHermanoCU,
)

# Autorizaciones de retiro
from .autorizaciones import (
    CrearAutorizacionRetiroCU,
    ListarAutorizacionesCU,
    VerificarAutorizacionCU,
    DesactivarAutorizacionCU,
    EliminarAutorizacionCU,
)

# Asistencia alumnos
from .asistencia_alumnos import (
    RegistrarEntradaAlumnoCU,
    RegistrarSalidaAlumnoCU,
    ListarAsistenciasAlumnoCU,
    ObtenerReporteAsistenciaAlumnoCU,
)

# Asistencia personal
from .asistencia_personal import (
    RegistrarEntradaPersonalCU,
    RegistrarSalidaPersonalCU,
    ListarAsistenciasPersonalCU,
    ObtenerReporteAsistenciaPersonalCU,
)

# Permisos personal
from .permisos import (
    SolicitarPermisoCU,
    AprobarPermisoCU,
    RechazarPermisoCU,
    ListarPermisosCU,
)

# Consentimientos
from .consentimientos import (
    CrearConsentimientosCU,
    ObtenerConsentimientosCU,
    ActualizarConsentimientosCU,
)

# Alumnos–paralelos
from .alumnos_paralelos import (
    AsignarAlumnoParaleloCU,
    ListarAlumnosParaleloCU,
    EliminarAsignacionParaleloCU,
)

__all__ = [
    # Alumnos
    "CrearAlumnoCU",
    "ObtenerAlumnoCU",
    "ActualizarAlumnoCU",
    "ListarAlumnosCU",
    "BuscarAlumnosCU",
    "EliminarAlumnoCU",
    # Tutores
    "CrearTutorCU",
    "ObtenerTutorCU",
    "ActualizarTutorCU",
    "BuscarTutoresCU",
    "EliminarTutorCU",
    # Relaciones
    "AsignarTutorAlumnoCU",
    "ListarTutoresAlumnoCU",
    "ActualizarRelacionTutorCU",
    "EliminarRelacionTutorCU",
    # Hermanos
    "RegistrarHermanoCU",
    "ListarHermanosCU",
    "ActualizarHermanoCU",
    "EliminarHermanoCU",
    # Autorizaciones
    "CrearAutorizacionRetiroCU",
    "ListarAutorizacionesCU",
    "VerificarAutorizacionCU",
    "DesactivarAutorizacionCU",
    "EliminarAutorizacionCU",
    # Asistencia alumnos
    "RegistrarEntradaAlumnoCU",
    "RegistrarSalidaAlumnoCU",
    "ListarAsistenciasAlumnoCU",
    "ObtenerReporteAsistenciaAlumnoCU",
    # Asistencia personal
    "RegistrarEntradaPersonalCU",
    "RegistrarSalidaPersonalCU",
    "ListarAsistenciasPersonalCU",
    "ObtenerReporteAsistenciaPersonalCU",
    # Permisos
    "SolicitarPermisoCU",
    "AprobarPermisoCU",
    "RechazarPermisoCU",
    "ListarPermisosCU",
    # Consentimientos
    "CrearConsentimientosCU",
    "ObtenerConsentimientosCU",
    "ActualizarConsentimientosCU",
    # Paralelos
    "AsignarAlumnoParaleloCU",
    "ListarAlumnosParaleloCU",
    "EliminarAsignacionParaleloCU",
    #Estadisticas
    "ObtenerEstadisticasParaleloUseCase",
    "ObtenerEstadisticasSedeUseCase",
    "ObtenerReporteFaltasUseCase",
    "ObtenerReporteRetrasosUseCase",
]

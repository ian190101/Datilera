# app/kernel/application/cursosextra/__init__.py

"""
Casos de Uso - Módulo Cursos Extra
"""

# Curso Extra
from .curso_extra import (
    CrearCursoExtra,
    CrearCursoExtraDTO,
    ActualizarCursoExtra,
    ActualizarCursoExtraDTO,
    ListarCursosExtra,
    ListarCursosExtraDTO,
    ObtenerCursoExtra,
    GestionarEstadoCurso,
)

# Inscripciones
from .inscripcion import (
    InscribirAlumnoInterno,
    InscribirAlumnoInternoDTO,
    InscribirAlumnoExterno,
    InscribirAlumnoExternoDTO,
    ListarInscripciones,
    ListarInscripcionesDTO,
    ObtenerInscripcion,
    GestionarEstadoInscripcion,
)

# Alumnos Externos
from .alumno_externo import (
    RegistrarAlumnoExterno,
    RegistrarAlumnoExternoDTO,
    ActualizarAlumnoExterno,
    ActualizarAlumnoExternoDTO,
    BuscarAlumnosExternos,
    BuscarAlumnosExternosDTO,
    ObtenerAlumnoExterno,
)

# Balance
from .balance import (
    CrearBalance,
    CrearBalanceDTO,
    ConsultarBalance,
    ListarBalances,
    ListarBalancesPendientesDTO,
)

# Pagos
from .pago import (
    RegistrarPago,
    RegistrarPagoDTO,
    ListarPagos,
    ListarPagosPorBalanceDTO,
    ConsultarPagosCurso,
    ConsultarPagosCursoDTO,
)

# Costos
from .costo import (
    RegistrarCosto,
    RegistrarCostoDTO,
    ActualizarCosto,
    ActualizarCostoDTO,
    EliminarCosto,
    ListarCostos,
    ListarCostosDTO,
)

# Categorías de Costo
from .categoria_costo import (
    CrearCategoriaCosto,
    CrearCategoriaCostoDTO,
    ActualizarCategoriaCosto,
    ActualizarCategoriaCostoDTO,
    GestionarEstadoCategoria,
    ListarCategoriasCosto,
    ListarCategoriasCostoDTO,
)

# Reportes
from .reportes import (
    GenerarReporteFinanciero,
    GenerarReporteFinancieroDTO,
    ReporteFinancieroResult,
    ObtenerBalanceCurso,
    ConsultarEstadisticas,
    EstadisticasCursoResult,
)

__all__ = [
    # Curso Extra
    "CrearCursoExtra",
    "CrearCursoExtraDTO",
    "ActualizarCursoExtra",
    "ActualizarCursoExtraDTO",
    "ListarCursosExtra",
    "ListarCursosExtraDTO",
    "ObtenerCursoExtra",
    "GestionarEstadoCurso",
    # Inscripciones
    "InscribirAlumnoInterno",
    "InscribirAlumnoInternoDTO",
    "InscribirAlumnoExterno",
    "InscribirAlumnoExternoDTO",
    "ListarInscripciones",
    "ListarInscripcionesDTO",
    "ObtenerInscripcion",
    "GestionarEstadoInscripcion",
    # Alumnos Externos
    "RegistrarAlumnoExterno",
    "RegistrarAlumnoExternoDTO",
    "ActualizarAlumnoExterno",
    "ActualizarAlumnoExternoDTO",
    "BuscarAlumnosExternos",
    "BuscarAlumnosExternosDTO",
    "ObtenerAlumnoExterno",
    # Balance
    "CrearBalance",
    "CrearBalanceDTO",
    "ConsultarBalance",
    "ListarBalances",
    "ListarBalancesPendientesDTO",
    # Pagos
    "RegistrarPago",
    "RegistrarPagoDTO",
    "ListarPagos",
    "ListarPagosPorBalanceDTO",
    "ConsultarPagosCurso",
    "ConsultarPagosCursoDTO",
    # Costos
    "RegistrarCosto",
    "RegistrarCostoDTO",
    "ActualizarCosto",
    "ActualizarCostoDTO",
    "EliminarCosto",
    "ListarCostos",
    "ListarCostosDTO",
    # Categorías de Costo
    "CrearCategoriaCosto",
    "CrearCategoriaCostoDTO",
    "ActualizarCategoriaCosto",
    "ActualizarCategoriaCostoDTO",
    "GestionarEstadoCategoria",
    "ListarCategoriasCosto",
    "ListarCategoriasCostoDTO",
    # Reportes
    "GenerarReporteFinanciero",
    "GenerarReporteFinancieroDTO",
    "ReporteFinancieroResult",
    "ObtenerBalanceCurso",
    "ConsultarEstadisticas",
    "EstadisticasCursoResult",
]

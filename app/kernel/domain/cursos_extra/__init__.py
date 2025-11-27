# app/kernel/domain/cursosextra/__init__.py

"""
Módulo de dominio: Cursos Extra

Incluye:
- Cursos extra con precios diferenciados y control de cupos
- Inscripciones de alumnos (internos y externos)
- Alumnos externos (no inscritos al centro)
- Balance y pagos por inscripción
- Costos y categorías de costos
- Consolidación de ingresos y cálculo de ganancias
"""

# Entidades
from .curso_extra_entidad import CursoExtra
from .inscripcion_curso_extra_entidad import (
    InscripcionCursoExtra,
    TipoAlumnoCursoExtra,
    EstadoInscripcionCursoExtra,
)
from .alumno_externo_entidad import AlumnoExterno
from .balance_curso_extra_entidad import BalanceCursoExtra, EstadoBalance
from .pago_curso_extra_entidad import PagoCursoExtra, MetodoPagoCursoExtra
from .costo_curso_extra_entidad import CostoCursoExtra
from .categoria_costo_curso_extra_entidad import CategoriaCostoCursoExtra
from .ingreso_curso_extra_entidad import IngresoCursoExtra

# Errors
from .errors import (
    CursosExtraError,
    # Cursos
    CursoExtraNoEncontrado,
    CursoExtraInactivo,
    CuposAgotados,
    NombreCursoInvalido,
    InstructorInvalido,
    FechasInvalidas,
    PorcentajeInvalido,
    CupoMaximoInvalido,
    PrecioInvalido,
    # Inscripciones
    InscripcionNoEncontrada,
    InscripcionDuplicada,
    InscripcionYaCompletada,
    InscripcionYaRetirada,
    TipoAlumnoInvalido,
    DatosAlumnoIncompletos,
    # Alumnos Externos
    AlumnoExternoNoEncontrado,
    AlumnoExternoDuplicado,
    NombreAlumnoInvalido,
    DatosTutorInvalidos,
    # Balance
    BalanceNoEncontrado,
    BalanceYaPagado,
    MontoInvalido,
    PagoExcedeSaldo,
    MontosPagoIncoherentes,
    # Pagos
    PagoNoEncontrado,
    PagoInmutable,
    MetodoPagoInvalido,
    ComprobanteRequerido,
    # Costos
    CostoNoEncontrado,
    CategoriaNoEncontrada,
    CategoriaDuplicada,
    CategoriaInactiva,
    CategoriaConCostos,
    DescripcionCostoInvalida,
    # Ingresos
    IngresoNoEncontrado,
    CalculoGananciasError,
    DatosFinancierosInconsistentes,
    # Validaciones
    SedeNoCoincide,
    SedeInvalida,
)

# Ports
from .ports import (
    # Repositorios
    CursoExtraRepositoryPort,
    InscripcionCursoExtraRepositoryPort,
    AlumnoExternoRepositoryPort,
    BalanceCursoExtraRepositoryPort,
    PagoCursoExtraRepositoryPort,
    CostoCursoExtraRepositoryPort,
    CategoriaCostoCursoExtraRepositoryPort,
    IngresoCursoExtraRepositoryPort,
)

__all__ = [
    # Entidades
    "CursoExtra",
    "InscripcionCursoExtra",
    "TipoAlumnoCursoExtra",
    "EstadoInscripcionCursoExtra",
    "AlumnoExterno",
    "BalanceCursoExtra",
    "EstadoBalance",
    "PagoCursoExtra",
    "MetodoPagoCursoExtra",
    "CostoCursoExtra",
    "CategoriaCostoCursoExtra",
    "IngresoCursoExtra",
    # Errors
    "CursosExtraError",
    # Cursos
    "CursoExtraNoEncontrado",
    "CursoExtraInactivo",
    "CuposAgotados",
    "NombreCursoInvalido",
    "InstructorInvalido",
    "FechasInvalidas",
    "PorcentajeInvalido",
    "CupoMaximoInvalido",
    "PrecioInvalido",
    # Inscripciones
    "InscripcionNoEncontrada",
    "InscripcionDuplicada",
    "InscripcionYaCompletada",
    "InscripcionYaRetirada",
    "TipoAlumnoInvalido",
    "DatosAlumnoIncompletos",
    # Alumnos Externos
    "AlumnoExternoNoEncontrado",
    "AlumnoExternoDuplicado",
    "NombreAlumnoInvalido",
    "DatosTutorInvalidos",
    # Balance
    "BalanceNoEncontrado",
    "BalanceYaPagado",
    "MontoInvalido",
    "PagoExcedeSaldo",
    "MontosPagoIncoherentes",
    # Pagos
    "PagoNoEncontrado",
    "PagoInmutable",
    "MetodoPagoInvalido",
    "ComprobanteRequerido",
    # Costos
    "CostoNoEncontrado",
    "CategoriaNoEncontrada",
    "CategoriaDuplicada",
    "CategoriaInactiva",
    "CategoriaConCostos",
    "DescripcionCostoInvalida",
    # Ingresos
    "IngresoNoEncontrado",
    "CalculoGananciasError",
    "DatosFinancierosInconsistentes",
    # Validaciones
    "SedeNoCoincide",
    "SedeInvalida",
    # Ports
    "CursoExtraRepositoryPort",
    "InscripcionCursoExtraRepositoryPort",
    "AlumnoExternoRepositoryPort",
    "BalanceCursoExtraRepositoryPort",
    "PagoCursoExtraRepositoryPort",
    "CostoCursoExtraRepositoryPort",
    "CategoriaCostoCursoExtraRepositoryPort",
    "IngresoCursoExtraRepositoryPort",
]

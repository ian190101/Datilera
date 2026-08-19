# app/infrastructure/db/models/__init__.py

"""
Punto de importación único de todos los modelos de la capa de persistencia.
Permite:
- Autodescubrimiento de tablas por Alembic (env.py puede importar este paquete).
- Tipado/linters mediante __all__.
"""

# Exponer Base si se necesita acceder a metadata desde aquí
from app.infrastructure.db.base import Base

# Seguridad
from .seguridad import (
    Sede,
    Usuario,
    Rol,
    Permiso,
    UsuarioRol,
    RolPermiso,
    Sesion,
    TokenRevocado,
    PreferenciaUsuario,
)

# Acceso (códigos para crear cuentas)
from .acceso import (
    CodigoAcceso,
    CodigoAccesoUso,
    EstadoCodigo,
)

# Académico
from .academico import (
    Grupo,
    Paralelo,
    ParaleloProfesora,
    Horario,
)

# Alumnos - CORREGIDO: quitar los enums que no existen
from .alumnos import (
    Alumno,
    Tutor,
    AlumnoTutor,
    AlumnoHermano,
    AutorizacionRetiro,
    AlumnoParalelo,
    AsistenciaAlumno,
    AsistenciaPersonal,
    Consentimiento,
    PermisoPersonal,
)

# Portafolio
from .portafolio import (
    Actividad,
    ActividadMedia,
    TipoMedia,
    ReporteDiario,
    ReporteLecturaTutor,
    PlanificacionProfesora,
)

# Inventario
from .inventario import (
    Familia,
    Categoria,
    Item,
    ItemAtributo,
    StockSede,
    MovimientoStock,
    TipoMovimiento as InvTipoMovimiento,
    PrestamoUniforme,
    AlertaStock,
    AlertaVencimiento,
)

from .exportacion import Exportacion

# Finanzas
from .finanzas import (
    CategoriaPago,
    CategoriaEgreso,
    Turno,  
    PrecioTurno,
    Pago,
    PagoCuota,
    Comprobante,
    Conciliacion,
    PlanPago,
    PlanCuota,
    EstadoCuentaNino,
    LibroCaja,
    Arqueo,
    Descuento,
    CuotaPlanPago,
    PlanPagoPersonalizado,
    Prorrateo

)

# Inscripción
from .inscripcion import (
    FormularioInscripcion,
    EstadoFormulario,
    FormularioRespuesta,
    DocumentoInscripcion,
    Firma,
    Contrato,
)

# Comunicaciones
from .comunicaciones import (
    Conversacion,
    TipoConversacion,
    Mensaje,
    TipoMensaje,
    MensajeAdjunto,
    TipoAdjunto,
    Notificacion,
    CanalNotificacion,
    EstadoNotificacion,
    NotificacionVista,
)


# IA
from .ia import IAConsulta

# Cursos extra
from .cursos_extra import (
    CursoExtra,
    InscripcionCursoExtra,
    EstadoInscripcionCursoExtra,
    CostoCursoExtra,
    BalanceCursoExtra,
    EstadoBalance,
)

# Auditoría
from .auditoria import AuditoriaAccion
from .calendario import TipoEvento, EventoCalendario, PlanificacionActividad

__all__ = [
    # Base
    "Base",
    # Seguridad
    "Sede", "Usuario", "Rol", "Permiso", "UsuarioRol", "RolPermiso",
    "Sesion", "TokenRevocado", "PreferenciaUsuario",
    # Acceso
    "CodigoAcceso", "CodigoAccesoUso", "EstadoCodigo",
    # Académico
    "Grupo", "Paralelo", "ParaleloProfesora", "Horario",
    # Alumnos - CORREGIDO
    "Alumno", "Tutor", "AlumnoTutor", "AlumnoHermano", "AutorizacionRetiro",
    "AlumnoParalelo",
    "AsistenciaAlumno", "AsistenciaPersonal",
    "Consentimiento", "PermisoPersonal",
    # Portafolio
    "Actividad", "ActividadMedia", "TipoMedia",
    "ReporteDiario", "ReporteLecturaTutor", "PlanificacionProfesora",
    # Inventario
    "Familia", "Categoria", "Item", "ItemAtributo",
    "StockSede", "MovimientoStock", "InvTipoMovimiento",
    "PrestamoUniforme", "AlertaStock", "AlertaVencimiento",
    #Exportacion
    "Exportacion",
    # Finanzas
    "CategoriaPago", "Turno", "PrecioTurno",
    "Pago", "PagoCuota", "Comprobante", "Conciliacion",
    "PlanPago", "PlanCuota",
    "EstadoCuentaNino", "LibroCaja",
    "Arqueo", "CategoriaEgreso",
    "Descuento",
    "PlanPagoPersonalizado",
    "CuotaPlanPago",
    "Prorrateo",
    # Inscripción
    "FormularioInscripcion", "EstadoFormulario",
    "FormularioRespuesta", "DocumentoInscripcion",
    "Firma", "Contrato",
    # Comunicaciones
    "Conversacion", "TipoConversacion",
    "Mensaje", "TipoMensaje",
    "MensajeAdjunto", "TipoAdjunto",
    "Notificacion", "CanalNotificacion", "EstadoNotificacion",
    "NotificacionVista",
    # Importaciones
    "ImportJob", "EstadoImportacion",
    # IA
    "IAConsulta",
    #Calendario
    "TipoEvento",
    "EventoCalendario",
    "PlanificacionActividad",
    # Cursos extra
    "CursoExtra", "InscripcionCursoExtra", "EstadoInscripcionCursoExtra",
    "CostoCursoExtra", "BalanceCursoExtra", "EstadoBalance",
    # Auditoría
    "AuditoriaAccion",
]

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
    HorarioParalelo,
)

# Alumnos
from .alumnos import (
    Alumno,
    AlumnoParalelo,
    AsistenciaAlumno,
    EstadoAsistenciaAlumno,
    AsistenciaPersonal,
    EstadoAsistenciaPersonal,
    Consentimiento,
    PermisoPersonal,
    EstadoPermiso,
)

# Portafolio
from .portafolio import (
    Actividad,
    ActividadMedia,
    TipoMedia,
    ReporteDiario,
    ReporteLecturaTutor,
)

# Inventario
from .inventario import (
    Familia,
    Categoria,
    Item,
    ItemAtributo,
    StockSede,
    MovimientoStock,
    TipoMovimiento as InvTipoMovimiento,  # evitar colisión de nombre
    PrestamoUniforme,
    AlertaStock,
    AlertaVencimiento,
)

# Finanzas (conjunto según estructura con categorías, turnos y planes)
from .finanzas import (
    CategoriaPago,
    Turno,
    PrecioTurno,
    Pago,
    Comprobante,
    Conciliacion,
    PlanPago,
    PlanCuota,
    EstadoCuota,
    EstadoCuentaNino,
    LibroCaja,
    TipoMovCaja,  # alias de TipoMovimiento de libro_caja
    Arqueo,
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

# Importaciones
from .importaciones import (
    ImportJob,
    EstadoImportacion,
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


__all__ = [
    # Base
    "Base",
    # Seguridad
    "Sede", "Usuario", "Rol", "Permiso", "UsuarioRol", "RolPermiso",
    "Sesion", "TokenRevocado", "PreferenciaUsuario",
    # Acceso
    "CodigoAcceso", "CodigoAccesoUso", "EstadoCodigo",
    # Académico
    "Grupo", "Paralelo", "ParaleloProfesora", "Horario", "HorarioParalelo",
    # Alumnos
    "Alumno", "AlumnoParalelo",
    "AsistenciaAlumno", "EstadoAsistenciaAlumno",
    "AsistenciaPersonal", "EstadoAsistenciaPersonal",
    "Consentimiento", "PermisoPersonal", "EstadoPermiso",
    # Portafolio
    "Actividad", "ActividadMedia", "TipoMedia",
    "ReporteDiario", "ReporteLecturaTutor",
    # Inventario
    "Familia", "Categoria", "Item", "ItemAtributo",
    "StockSede", "MovimientoStock", "InvTipoMovimiento",
    "PrestamoUniforme", "AlertaStock", "AlertaVencimiento",
    # Finanzas
    "CategoriaPago", "Turno", "PrecioTurno",
    "Pago", "Comprobante", "Conciliacion",
    "PlanPago", "PlanCuota", "EstadoCuota",
    "EstadoCuentaNino", "LibroCaja", "TipoMovCaja",
    "Arqueo",
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
    # Cursos extra
    "CursoExtra", "InscripcionCursoExtra", "EstadoInscripcionCursoExtra",
    "CostoCursoExtra", "BalanceCursoExtra", "EstadoBalance",
    # Auditoría
    "AuditoriaAccion",
]

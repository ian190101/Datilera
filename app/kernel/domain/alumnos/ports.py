# app/kernel/domain/alumnos/ports.py
from __future__ import annotations

from typing import Protocol, Optional, Sequence, AsyncContextManager, runtime_checkable
from datetime import date, datetime, time

from .alumno_entidad import Alumno
from .alumno_paralelo_entidad import AlumnoParalelo
from .asistencia_alumno_entidad import AsistenciaAlumno  # estados: PRESENTE, FALTA, RETRASO
from .consentimiento_entidad import Consentimiento       # consentimiento imágenes/datos (único, con historial)
from .asistencia_personal_entidad import AsistenciaPersonal  # P/F/R para personal
from .permiso_personal_entidad import PermisoPersonal        # solicitud con estados: PENDIENTE/APROBADO/RECHAZADO


# =========================
# Alumnos
# =========================
@runtime_checkable
class AlumnoRepo(Protocol):
    """
    Puerto de acceso a Alumnos.

    Convenciones:
    - `guardar` aplica upsert (inserta/actualiza) y NO confirma cambios (lo hace el UoW).
    - Evitar propagar errores de DB; traducir a errores de dominio (ver errors.py).
    - Soporte de soft-delete opcional vía `desactivar/activar` si tu entidad lo contempla.
    """

    # --- Lectura ---
    async def obtener(self, alumno_id: int) -> Optional[Alumno]:
        """Retorna el alumno por id o None si no existe."""
        ...

    async def listar_por_sede(
        self,
        sede_id: int,
        *,
        texto: Optional[str] = None,  # búsqueda por nombre/CI/etc.
        limit: int = 100,
        offset: int = 0,
    ) -> Sequence[Alumno]:
        """Lista alumnos de una sede con filtros y paginación."""
        ...

    async def listar_por_paralelo(
        self,
        paralelo_id: int,
        *,
        limit: int = 100,
        offset: int = 0,
    ) -> Sequence[Alumno]:
        """Lista alumnos asignados actualmente a un paralelo."""
        ...

    # --- Escritura ---
    async def guardar(self, alumno: Alumno) -> None:
        """Inserta o actualiza el alumno. No hace commit."""
        ...

    async def desactivar(self, alumno_id: int, *, motivo: Optional[str] = None) -> None:
        """Soft-delete/desactivación (si aplica)."""
        ...

    async def activar(self, alumno_id: int) -> None:
        """Reactivación (si aplica)."""
        ...

    async def next_id(self) -> int:
        """
        (Opcional) Próximo id disponible si el adaptador lo soporta.
        Si usas autoincrement/UUID en DB, puedes no implementarlo (stub/NotImplementedError).
        """
        ...


# =========================
# Asignación Alumno-Paralelo (histórico)
# =========================
@runtime_checkable
class AlumnoParaleloRepo(Protocol):
    """
    Puerto para gestionar la relación Alumno-Paralelo (actual e histórico).
    Debe respetar cupos máximos por paralelo (regla de negocio).
    """

    async def obtener_actual_por_alumno(self, alumno_id: int) -> Optional[AlumnoParalelo]:
        """Devuelve la asignación vigente del alumno si existe."""
        ...

    async def historico_por_alumno(
        self,
        alumno_id: int,
        *,
        limit: int = 100,
        offset: int = 0,
    ) -> Sequence[AlumnoParalelo]:
        """Histórico completo de paralelos por alumno."""
        ...

    async def listar_por_paralelo(
        self,
        paralelo_id: int,
        *,
        en_fecha: Optional[date] = None,  # si quieres ver quiénes estaban asignados en una fecha
        limit: int = 100,
        offset: int = 0,
    ) -> Sequence[AlumnoParalelo]:
        """Listado (actual o en una fecha) de asignaciones de un paralelo."""
        ...

    async def asignar(self, asignacion: AlumnoParalelo) -> None:
        """
        Asigna el alumno a un paralelo (inicio de vigencia).
        Debe validar cupo y reglas del dominio. No hace commit.
        """
        ...

    async def finalizar_asignacion(
        self,
        alumno_id: int,
        *,
        fecha_fin: date,
        motivo: Optional[str] = None,
    ) -> None:
        """Cierra la asignación vigente del alumno (si existe)."""
        ...

    async def transferir(
        self,
        alumno_id: int,
        nuevo_paralelo_id: int,
        *,
        fecha_desde: date,
        motivo: Optional[str] = None,
    ) -> None:
        """
        Transferencia atómica: cierra asignación vigente y crea una nueva en `nuevo_paralelo_id`.
        Debe validar cupo y no solapar vigencias.
        """
        ...

    # Ayudas opcionales para reglas de cupo
    async def contar_asignados(self, paralelo_id: int, *, en_fecha: Optional[date] = None) -> int:
        """Cantidad de alumnos asignados (ahora o en una fecha)."""
        ...


# =========================
# Asistencia de Alumnos
# =========================
@runtime_checkable
class AsistenciaAlumnoRepo(Protocol):
    """
    Puerto para registrar/consultar asistencia de alumnos.
    Estados típicos: PRESENTE, FALTA, RETRASO. Para RETRASO se registra `hora_retraso`.
    """

    async def registrar(self, asistencia: AsistenciaAlumno) -> None:
        """
        Crea el registro de asistencia para un alumno en una fecha (y paralelo si aplica).
        No hace commit. Debe aplicar reglas anti-duplicado por (alumno, fecha).
        """
        ...

    async def actualizar_estado(
        self,
        asistencia_id: int,
        *,
        estado: str,                     # 'PRESENTE' | 'FALTA' | 'RETRASO'
        hora_retraso: Optional[time] = None,
    ) -> None:
        """Actualiza el estado (y hora de retraso si corresponde)."""
        ...

    async def obtener(self, asistencia_id: int) -> Optional[AsistenciaAlumno]:
        """Obtiene un registro de asistencia por id."""
        ...

    async def listar_por_alumno(
        self,
        alumno_id: int,
        *,
        desde: Optional[date] = None,
        hasta: Optional[date] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> Sequence[AsistenciaAlumno]:
        """Listado por alumno en un rango de fechas."""
        ...

    async def listar_por_paralelo_en_fecha(
        self,
        paralelo_id: int,
        fecha: date,
        *,
        limit: int = 100,
        offset: int = 0,
    ) -> Sequence[AsistenciaAlumno]:
        """Listado de asistencias de un paralelo en una fecha específica."""
        ...


# =========================
# Consentimientos (imágenes/datos)
# =========================
@runtime_checkable
class ConsentimientoRepo(Protocol):
    """
    Puerto para gestionar consentimientos del alumno.
    Según tus historias: un consentimiento global (sin vigencia ni revocación),
    pero con auditoría/histórico de cambios.
    """

    async def obtener_actual(self, alumno_id: int) -> Optional[Consentimiento]:
        """Retorna el consentimiento vigente (último) del alumno, si existe."""
        ...

    async def guardar(self, consentimiento: Consentimiento) -> None:
        """Inserta un nuevo consentimiento (o actualización) y mantiene historial. No hace commit."""
        ...

    async def historico_por_alumno(
        self,
        alumno_id: int,
        *,
        limit: int = 100,
        offset: int = 0,
    ) -> Sequence[Consentimiento]:
        """Devuelve el historial de consentimientos del alumno."""
        ...


# =========================
# Asistencia del Personal (profesoras/auxiliares)
# =========================
@runtime_checkable
class AsistenciaPersonalRepo(Protocol):
    """
    Puerto para asistencia del personal (profesoras/auxiliares) con P/F/R.
    """

    async def registrar(self, asistencia: AsistenciaPersonal) -> None:
        """Crea el registro de asistencia del personal (no hace commit)."""
        ...

    async def actualizar_estado(
        self,
        asistencia_id: int,
        *,
        estado: str,                  # 'PRESENTE' | 'FALTA' | 'RETRASO'
        hora_retraso: Optional[time] = None,
    ) -> None:
        """Actualiza el estado de asistencia del personal."""
        ...

    async def listar_por_personal(
        self,
        personal_id: int,
        *,
        desde: Optional[date] = None,
        hasta: Optional[date] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> Sequence[AsistenciaPersonal]:
        """Listado por persona en rango de fechas."""
        ...

    async def listar_por_sede_en_fecha(
        self,
        sede_id: int,
        fecha: date,
        *,
        limit: int = 100,
        offset: int = 0,
    ) -> Sequence[AsistenciaPersonal]:
        """Listado de asistencias de personal de una sede en una fecha."""
        ...


# =========================
# Permisos del Personal (bajas médicas/permiso)
# =========================
@runtime_checkable
class PermisoPersonalRepo(Protocol):
    """
    Puerto para solicitudes de permiso del personal.
    Flujo: creación (PENDIENTE) -> aprobación (APROBADO) o rechazo (RECHAZADO).
    Debe soportar adjunto (pdf/imagen) a nivel de entidad.
    """

    async def obtener(self, permiso_id: int) -> Optional[PermisoPersonal]:
        """Obtiene una solicitud por id."""
        ...

    async def guardar(self, permiso: PermisoPersonal) -> None:
        """Crea/actualiza una solicitud (queda PENDIENTE). No hace commit."""
        ...

    async def aprobar(
        self,
        permiso_id: int,
        *,
        aprobado_por: int,
        observacion: Optional[str] = None,
        fecha_decision: Optional[datetime] = None,
    ) -> None:
        """Aprueba la solicitud (cambia estado y registra auditoría)."""
        ...

    async def rechazar(
        self,
        permiso_id: int,
        *,
        rechazado_por: int,
        observacion: Optional[str] = None,
        fecha_decision: Optional[datetime] = None,
    ) -> None:
        """Rechaza la solicitud (cambia estado y registra auditoría)."""
        ...

    async def listar_por_personal(
        self,
        personal_id: int,
        *,
        estados: Optional[Sequence[str]] = None,  # ['PENDIENTE', 'APROBADO', 'RECHAZADO']
        desde: Optional[date] = None,
        hasta: Optional[date] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> Sequence[PermisoPersonal]:
        """Lista permisos por persona, con filtros y paginación."""
        ...

    async def listar_pendientes_por_sede(
        self,
        sede_id: int,
        *,
        limit: int = 100,
        offset: int = 0,
    ) -> Sequence[PermisoPersonal]:
        """Lista permisos en estado PENDIENTE para revisión por sede."""
        ...


# =========================
# Unit of Work
# =========================
@runtime_checkable
class UnitOfWork(Protocol, AsyncContextManager["UnitOfWork"]):
    """
    Unidad de Trabajo asíncrona para el subdominio Alumnos.

    Política: COMMIT EXPLÍCITO (Patrón B)
    - `__aexit__` hace rollback si hubo excepción; si no hubo, NO hace commit automático.
    - Los servicios de aplicación deben invocar `await uow.commit()` en el caso feliz.
    """

    alumnos: AlumnoRepo
    alumno_paralelos: AlumnoParaleloRepo
    asistencias_alumnos: AsistenciaAlumnoRepo
    consentimientos: ConsentimientoRepo

    # Incluidos porque ya tienes las entidades en este paquete y están en las historias:
    asistencias_personal: AsistenciaPersonalRepo
    permisos_personal: PermisoPersonalRepo

    async def __aenter__(self) -> UnitOfWork: ...
    async def __aexit__(self, exc_type, exc, tb) -> None: ...

    async def commit(self) -> None:
        """Confirma la transacción actual."""
        ...

    async def rollback(self) -> None:
        """Revierte la transacción actual."""
        ...

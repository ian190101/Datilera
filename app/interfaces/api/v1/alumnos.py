# app/interfaces/api/v1/alumnos.py

from __future__ import annotations

from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.session import get_session

# Repositorios
from app.infrastructure.db.repositories.alumnos.alumnos_repo import AlumnosRepository
from app.infrastructure.db.repositories.alumnos.tutores_repo import TutoresRepository
from app.infrastructure.db.repositories.alumnos.alumnos_tutores_repo import AlumnosTutoresRepository
from app.infrastructure.db.repositories.alumnos.alumnos_hermanos_repo import AlumnosHermanosRepository
from app.infrastructure.db.repositories.alumnos.autorizaciones_retiro_repo import AutorizacionesRetiroRepository
from app.infrastructure.db.repositories.alumnos.asistencia_alumnos_repo import AsistenciaAlumnosRepository
from app.infrastructure.db.repositories.alumnos.asistencia_personal_repo import AsistenciaPersonalRepository
from app.infrastructure.db.repositories.alumnos.permisos_personal_repo import PermisosPersonalRepository
from app.infrastructure.db.repositories.alumnos.consentimientos_repo import ConsentimientosRepository
from app.infrastructure.db.repositories.alumnos.alumnos_paralelos_repo import AlumnosParalelosRepository

# Casos de uso
from app.kernel.application.alumnos import (
    # Alumnos
    CrearAlumnoCU,
    ObtenerAlumnoCU,
    ActualizarAlumnoCU,
    ListarAlumnosCU,
    BuscarAlumnosCU,
    EliminarAlumnoCU,
    # Tutores
    CrearTutorCU,
    ObtenerTutorCU,
    ActualizarTutorCU,
    BuscarTutoresCU,
    EliminarTutorCU,
    # Relaciones
    AsignarTutorAlumnoCU,
    ListarTutoresAlumnoCU,
    ActualizarRelacionTutorCU,
    EliminarRelacionTutorCU,
    # Hermanos
    RegistrarHermanoCU,
    ListarHermanosCU,
    ActualizarHermanoCU,
    EliminarHermanoCU,
    # Autorizaciones
    CrearAutorizacionRetiroCU,
    ListarAutorizacionesCU,
    VerificarAutorizacionCU,
    DesactivarAutorizacionCU,
    EliminarAutorizacionCU,
    # Asistencia alumnos
    RegistrarEntradaAlumnoCU,
    RegistrarSalidaAlumnoCU,
    ListarAsistenciasAlumnoCU,
    ObtenerReporteAsistenciaAlumnoCU,
    # Asistencia personal
    RegistrarEntradaPersonalCU,
    RegistrarSalidaPersonalCU,
    ListarAsistenciasPersonalCU,
    ObtenerReporteAsistenciaPersonalCU,
    # Permisos
    SolicitarPermisoCU,
    AprobarPermisoCU,
    RechazarPermisoCU,
    ListarPermisosCU,
    # Consentimientos
    CrearConsentimientosCU,
    ObtenerConsentimientosCU,
    ActualizarConsentimientosCU,
    # Paralelos
    AsignarAlumnoParaleloCU,
    ListarAlumnosParaleloCU,
    EliminarAsignacionParaleloCU,
    #Estadisticas
    ObtenerReporteRetrasosUseCase,
    ObtenerReporteFaltasUseCase,
    ObtenerEstadisticasParaleloUseCase,
    ObtenerEstadisticasSedeUseCase,
)

router = APIRouter(prefix="/alumnos", tags=["Alumnos"])

SessionDep = Annotated[AsyncSession, Depends(get_session)]

# Helpers DI
def alumnos_repo(db: AsyncSession) -> AlumnosRepository: return AlumnosRepository(db)
def tutores_repo(db: AsyncSession) -> TutoresRepository: return TutoresRepository(db)
def rel_repo(db: AsyncSession) -> AlumnosTutoresRepository: return AlumnosTutoresRepository(db)
def hermanos_repo(db: AsyncSession) -> AlumnosHermanosRepository: return AlumnosHermanosRepository(db)
def aut_repo(db: AsyncSession) -> AutorizacionesRetiroRepository: return AutorizacionesRetiroRepository(db)
def asis_alum_repo(db: AsyncSession) -> AsistenciaAlumnosRepository: return AsistenciaAlumnosRepository(db)
def asis_pers_repo(db: AsyncSession) -> AsistenciaPersonalRepository: return AsistenciaPersonalRepository(db)
def permisos_repo(db: AsyncSession) -> PermisosPersonalRepository: return PermisosPersonalRepository(db)
def cons_repo(db: AsyncSession) -> ConsentimientosRepository: return ConsentimientosRepository(db)
def paralelos_repo(db: AsyncSession) -> AlumnosParalelosRepository: return AlumnosParalelosRepository(db)

# ---------------------------------------------------------------------------
# ALUMNOS
# ---------------------------------------------------------------------------

@router.post("", status_code=status.HTTP_201_CREATED)
async def crear_alumno(
    db: SessionDep,
    # payload: CrearAlumnoRequest,
):
    uc = CrearAlumnoCU(alumnos_repo(db))
    # return await uc.ejecutar(**payload.model_dump())
    return {"detail": "TODO implementar DTO creación alumno"}


@router.get("/{alumno_id}")
async def obtener_alumno(alumno_id: int, db: SessionDep):
    uc = ObtenerAlumnoCU(alumnos_repo(db))
    return await uc.por_id(alumno_id)


@router.get("/codigo/{codigo}")
async def obtener_alumno_por_codigo(codigo: str, db: SessionDep):
    uc = ObtenerAlumnoCU(alumnos_repo(db))
    return await uc.por_codigo(codigo)


@router.get("/documento/{numero}")
async def obtener_alumno_por_documento(numero: str, db: SessionDep):
    uc = ObtenerAlumnoCU(alumnos_repo(db))
    return await uc.por_documento(numero)


@router.get("")
async def listar_alumnos(
    sede_id: int,
    db: SessionDep,
    solo_activos: bool = True,
):
    uc = ListarAlumnosCU(alumnos_repo(db))
    return await uc.por_sede(sede_id, solo_activos)


@router.get("/buscar")
async def buscar_alumnos(
    termino: str,
    db: SessionDep,
    sede_id: int | None = None,
):
    uc = BuscarAlumnosCU(alumnos_repo(db))
    return await uc.ejecutar(termino, sede_id)


@router.put("/{alumno_id}", status_code=status.HTTP_204_NO_CONTENT)
async def actualizar_alumno(
    alumno_id: int,
    db: SessionDep,
    # payload: ActualizarAlumnoRequest,
):
    uc = ActualizarAlumnoCU(alumnos_repo(db))
    # await uc.ejecutar(alumno_id, **payload.model_dump(exclude_unset=True))
    return None


@router.delete("/{alumno_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_alumno(alumno_id: int, db: SessionDep):
    uc = EliminarAlumnoCU(alumnos_repo(db))
    await uc.ejecutar(alumno_id)
    return None

# ---------------------------------------------------------------------------
# TUTORES
# ---------------------------------------------------------------------------

@router.post("/tutores", status_code=status.HTTP_201_CREATED)
async def crear_tutor(
    db: SessionDep,
    # payload: CrearTutorRequest,
):
    uc = CrearTutorCU(tutores_repo(db))
    # return await uc.ejecutar(**payload.model_dump())
    return {"detail": "TODO implementar DTO creación tutor"}


@router.get("/tutores/{tutor_id}")
async def obtener_tutor(tutor_id: int, db: SessionDep):
    uc = ObtenerTutorCU(tutores_repo(db))
    return await uc.por_id(tutor_id)


@router.get("/tutores/documento/{documento}")
async def obtener_tutor_por_documento(documento: str, db: SessionDep):
    uc = ObtenerTutorCU(tutores_repo(db))
    return await uc.por_documento(documento)


@router.get("/tutores")
async def buscar_tutores(termino: str, db: SessionDep):
    uc = BuscarTutoresCU(tutores_repo(db))
    return await uc.ejecutar(termino)


@router.put("/tutores/{tutor_id}", status_code=status.HTTP_204_NO_CONTENT)
async def actualizar_tutor(
    tutor_id: int,
    db: SessionDep,
    # payload: ActualizarTutorRequest,
):
    uc = ActualizarTutorCU(tutores_repo(db))
    # await uc.ejecutar(tutor_id, **payload.model_dump(exclude_unset=True))
    return None


@router.delete("/tutores/{tutor_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_tutor(tutor_id: int, db: SessionDep):
    uc = EliminarTutorCU(tutores_repo(db))
    await uc.ejecutar(tutor_id)
    return None

# ---------------------------------------------------------------------------
# RELACIONES ALUMNO–TUTOR
# ---------------------------------------------------------------------------

@router.post("/relaciones", status_code=status.HTTP_201_CREATED)
async def asignar_tutor_alumno(
    db: SessionDep,
    # payload: AsignarTutorAlumnoRequest,
):
    uc = AsignarTutorAlumnoCU(alumnos_repo(db), tutores_repo(db), rel_repo(db))
    # return await uc.ejecutar(**payload.model_dump())
    return {"detail": "TODO implementar DTO asignar tutor"}


@router.get("/{alumno_id}/tutores")
async def listar_tutores_de_alumno(alumno_id: int, db: SessionDep):
    uc = ListarTutoresAlumnoCU(rel_repo(db))
    return await uc.ejecutar(alumno_id)


@router.put("/relaciones/{relacion_id}", status_code=status.HTTP_204_NO_CONTENT)
async def actualizar_relacion(
    relacion_id: int,
    db: SessionDep,
    # payload: ActualizarRelacionRequest,
):
    uc = ActualizarRelacionTutorCU(rel_repo(db))
    # await uc.ejecutar(relacion_id, **payload.model_dump(exclude_unset=True))
    return None


@router.delete("/relaciones/{relacion_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_relacion(relacion_id: int, db: SessionDep):
    uc = EliminarRelacionTutorCU(rel_repo(db))
    await uc.ejecutar(relacion_id)
    return None

# ---------------------------------------------------------------------------
# HERMANOS
# ---------------------------------------------------------------------------

@router.post("/{alumno_id}/hermanos", status_code=status.HTTP_201_CREATED)
async def registrar_hermano(
    alumno_id: int,
    db: SessionDep,
    # payload: RegistrarHermanoRequest,
):
    uc = RegistrarHermanoCU(alumnos_repo(db), hermanos_repo(db))
    # return await uc.ejecutar(alumno_id, **payload.model_dump())
    return {"detail": "TODO implementar DTO registrar hermano"}


@router.get("/{alumno_id}/hermanos")
async def listar_hermanos(alumno_id: int, db: SessionDep):
    uc = ListarHermanosCU(hermanos_repo(db))
    return await uc.ejecutar(alumno_id)


@router.put("/hermanos/{hermano_id}", status_code=status.HTTP_204_NO_CONTENT)
async def actualizar_hermano(
    hermano_id: int,
    db: SessionDep,
    # payload: ActualizarHermanoRequest,
):
    uc = ActualizarHermanoCU(hermanos_repo(db))
    # await uc.ejecutar(hermano_id, **payload.model_dump(exclude_unset=True))
    return None


@router.delete("/hermanos/{hermano_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_hermano(hermano_id: int, db: SessionDep):
    uc = EliminarHermanoCU(hermanos_repo(db))
    await uc.ejecutar(hermano_id)
    return None

# ---------------------------------------------------------------------------
# AUTORIZACIONES DE RETIRO
# ---------------------------------------------------------------------------

@router.post("/{alumno_id}/autorizaciones-retiro", status_code=status.HTTP_201_CREATED)
async def crear_autorizacion_retiro(
    alumno_id: int,
    db: SessionDep,
    # payload: CrearAutorizacionRetiroRequest,
):
    uc = CrearAutorizacionRetiroCU(alumnos_repo(db), aut_repo(db))
    # return await uc.ejecutar(alumno_id, **payload.model_dump())
    return {"detail": "TODO implementar DTO crear autorización retiro"}


@router.get("/{alumno_id}/autorizaciones-retiro")
async def listar_autorizaciones_retiro(
    alumno_id: int,
    db: SessionDep,
    solo_activas: bool = True,
):
    uc = ListarAutorizacionesCU(aut_repo(db))
    return await uc.ejecutar(alumno_id, solo_activas)


@router.get("/{alumno_id}/autorizaciones-retiro/ci/{ci_numero}")
async def verificar_autorizacion(alumno_id: int, ci_numero: str, db: SessionDep):
    uc = VerificarAutorizacionCU(aut_repo(db))
    return await uc.ejecutar(alumno_id, ci_numero)


@router.put("/autorizaciones-retiro/{autorizacion_id}/desactivar", status_code=status.HTTP_204_NO_CONTENT)
async def desactivar_autorizacion(autorizacion_id: int, db: SessionDep):
    uc = DesactivarAutorizacionCU(aut_repo(db))
    await uc.ejecutar(autorizacion_id)
    return None


@router.delete("/autorizaciones-retiro/{autorizacion_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_autorizacion(autorizacion_id: int, db: SessionDep):
    uc = EliminarAutorizacionCU(aut_repo(db))
    await uc.ejecutar(autorizacion_id)
    return None

# ---------------------------------------------------------------------------
# ASISTENCIA ALUMNOS
# ---------------------------------------------------------------------------

@router.post("/{alumno_id}/asistencia/entrada", status_code=status.HTTP_201_CREATED)
async def registrar_entrada_alumno(
    alumno_id: int,
    db: SessionDep,
    # payload: RegistrarEntradaAlumnoRequest,
):
    uc = RegistrarEntradaAlumnoCU(asis_alum_repo(db))
    # return await uc.ejecutar(alumno_id=alumno_id, **payload.model_dump())
    return {"detail": "TODO implementar DTO registrar entrada alumno"}


@router.post("/{alumno_id}/asistencia/salida", status_code=status.HTTP_201_CREATED)
async def registrar_salida_alumno(
    alumno_id: int,
    db: SessionDep,
    # payload: RegistrarSalidaAlumnoRequest,
):
    uc = RegistrarSalidaAlumnoCU(asis_alum_repo(db))
    # return await uc.ejecutar(alumno_id=alumno_id, **payload.model_dump())
    return {"detail": "TODO implementar DTO registrar salida alumno"}


@router.get("/{alumno_id}/asistencia")
async def listar_asistencia_alumno(
    alumno_id: int,
    db: SessionDep,
    fecha_desde: date | None = None,
    fecha_hasta: date | None = None,
):
    uc = ListarAsistenciasAlumnoCU(asis_alum_repo(db))
    return await uc.ejecutar(alumno_id, fecha_desde, fecha_hasta)


@router.get("/{alumno_id}/asistencia/reporte")
async def reporte_asistencia_alumno(
    alumno_id: int,
    fecha_desde: date,
    fecha_hasta: date,
    db: SessionDep,
):
    uc = ObtenerReporteAsistenciaAlumnoCU(asis_alum_repo(db))
    return await uc.ejecutar(alumno_id, fecha_desde, fecha_hasta)

# ---------------------------------------------------------------------------
# ASISTENCIA PERSONAL
# ---------------------------------------------------------------------------

@router.post("/personal/{personal_id}/asistencia/entrada", status_code=status.HTTP_201_CREATED)
async def registrar_entrada_personal(
    personal_id: int,
    db: SessionDep,
    # payload: RegistrarEntradaPersonalRequest,
):
    uc = RegistrarEntradaPersonalCU(asis_pers_repo(db))
    # return await uc.ejecutar(personal_id=personal_id, **payload.model_dump())
    return {"detail": "TODO implementar DTO registrar entrada personal"}


@router.post("/personal/{personal_id}/asistencia/salida", status_code=status.HTTP_201_CREATED)
async def registrar_salida_personal(
    personal_id: int,
    db: SessionDep,
    # payload: RegistrarSalidaPersonalRequest,
):
    uc = RegistrarSalidaPersonalCU(asis_pers_repo(db))
    # return await uc.ejecutar(personal_id=personal_id, **payload.model_dump())
    return {"detail": "TODO implementar DTO registrar salida personal"}


@router.get("/sede/{sede_id}/asistencia-personal")
async def listar_asistencia_personal(
    sede_id: int,
    fecha: date,
    db: SessionDep,
):
    uc = ListarAsistenciasPersonalCU(asis_pers_repo(db))
    return await uc.ejecutar(sede_id, fecha)


@router.get("/sede/{sede_id}/asistencia-personal/reporte")
async def reporte_asistencia_personal(
    sede_id: int,
    fecha_inicio: date,
    fecha_fin: date,
    db: SessionDep,
):
    uc = ObtenerReporteAsistenciaPersonalCU(asis_pers_repo(db))
    return await uc.ejecutar(sede_id, fecha_inicio, fecha_fin)

# ---------------------------------------------------------------------------
# PERMISOS PERSONAL
# ---------------------------------------------------------------------------

@router.post("/permisos-personal", status_code=status.HTTP_201_CREATED)
async def solicitar_permiso(
    db: SessionDep,
    # payload: SolicitarPermisoRequest,
):
    uc = SolicitarPermisoCU(permisos_repo(db))
    # return await uc.ejecutar(**payload.model_dump())
    return {"detail": "TODO implementar DTO solicitar permiso"}


@router.put("/permisos-personal/{permiso_id}/aprobar", status_code=status.HTTP_204_NO_CONTENT)
async def aprobar_permiso(
    permiso_id: int,
    aprobado_por_id: int,
    db: SessionDep,
):
    uc = AprobarPermisoCU(permisos_repo(db))
    await uc.ejecutar(permiso_id, aprobado_por_id)
    return None


@router.put("/permisos-personal/{permiso_id}/rechazar", status_code=status.HTTP_204_NO_CONTENT)
async def rechazar_permiso(
    permiso_id: int,
    aprobado_por_id: int,
    db: SessionDep,
):
    uc = RechazarPermisoCU(permisos_repo(db))
    await uc.ejecutar(permiso_id, aprobado_por_id)
    return None


@router.get("/sede/{sede_id}/permisos-personal")
async def listar_permisos_sede(
    sede_id: int,
    db: SessionDep,
    estado: str | None = None,
):
    uc = ListarPermisosCU(permisos_repo(db))
    return await uc.por_sede(sede_id, estado)


@router.get("/personal/{personal_id}/permisos-personal")
async def listar_permisos_personal(personal_id: int, db: SessionDep):
    uc = ListarPermisosCU(permisos_repo(db))
    return await uc.por_personal(personal_id)

# ---------------------------------------------------------------------------
# CONSENTIMIENTOS
# ---------------------------------------------------------------------------

@router.post("/{alumno_id}/consentimientos", status_code=status.HTTP_201_CREATED)
async def crear_o_actualizar_consentimientos(
    alumno_id: int,
    db: SessionDep,
    # payload: CrearOActualizarConsentimientosRequest,
):
    uc = CrearConsentimientosCU(cons_repo(db))
    # return await uc.ejecutar(alumno_id, **payload.model_dump())
    return {"detail": "TODO implementar DTO consentimientos"}


@router.get("/{alumno_id}/consentimientos")
async def obtener_consentimientos(alumno_id: int, db: SessionDep):
    uc = ObtenerConsentimientosCU(cons_repo(db))
    return await uc.ejecutar(alumno_id)


@router.put("/{alumno_id}/consentimientos", status_code=status.HTTP_204_NO_CONTENT)
async def actualizar_consentimientos(
    alumno_id: int,
    db: SessionDep,
    # payload: ActualizarConsentimientosRequest,
):
    uc = ActualizarConsentimientosCU(cons_repo(db))
    # await uc.ejecutar(alumno_id, **payload.model_dump())
    return None

# ---------------------------------------------------------------------------
# ALUMNOS – PARALELOS
# ---------------------------------------------------------------------------

@router.post("/paralelos/asignar", status_code=status.HTTP_201_CREATED)
async def asignar_alumno_paralelo(
    db: SessionDep,
    # payload: AsignarAlumnoParaleloRequest,
):
    uc = AsignarAlumnoParaleloCU(alumnos_repo(db), paralelos_repo(db))
    # return await uc.ejecutar(**payload.model_dump())
    return {"detail": "TODO implementar DTO asignación paralelo"}


@router.get("/paralelos/{paralelo_id}/alumnos")
async def listar_alumnos_de_paralelo(paralelo_id: int, db: SessionDep):
    uc = ListarAlumnosParaleloCU(paralelos_repo(db))
    return await uc.ejecutar(paralelo_id)


@router.delete("/paralelos/asignaciones/{asignacion_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_asignacion_paralelo(asignacion_id: int, db: SessionDep):
    uc = EliminarAsignacionParaleloCU(paralelos_repo(db))
    await uc.ejecutar(asignacion_id)
    return None

# ---------------------------------------------------------------------------
# ESTADÍSTICAS DE ASISTENCIA
# ---------------------------------------------------------------------------

@router.get("/asistencia/estadisticas/paralelo/{paralelo_id}")
async def obtener_estadisticas_paralelo(
    paralelo_id: int,
    fecha_inicio: date,
    fecha_fin: date,
    db: SessionDep,
):
    """Obtener estadísticas de asistencia de un paralelo.
    
    Retorna contadores de presentes, tardanzas, ausentes y porcentajes.
    """
    from app.kernel.application.alumnos.estadisticas import (
        ObtenerEstadisticasParaleloUseCase
    )
    
    uc = ObtenerEstadisticasParaleloUseCase(asis_alum_repo(db))
    return await uc.ejecutar(paralelo_id, fecha_inicio, fecha_fin)


@router.get("/asistencia/estadisticas/sede/{sede_id}")
async def obtener_estadisticas_sede(
    sede_id: int,
    fecha_inicio: date,
    fecha_fin: date,
    db: SessionDep,
):
    """Obtener estadísticas de asistencia de una sede.
    
    Retorna estadísticas globales de todos los paralelos de la sede.
    """
    from app.kernel.application.alumnos.estadisticas import (
        ObtenerEstadisticasSedeUseCase
    )
    
    uc = ObtenerEstadisticasSedeUseCase(asis_alum_repo(db))
    return await uc.ejecutar(sede_id, fecha_inicio, fecha_fin)


@router.get("/asistencia/retrasos/reporte")
async def obtener_reporte_retrasos(
    sede_id: int,
    fecha_inicio: date,
    fecha_fin: date,
    db: SessionDep,
    limite: int = 100,
):
    """Obtener reporte de retrasos.
    
    Lista todos los registros de asistencia con estado='tarde'.
    Útil para seguimiento y notificaciones a tutores.
    """
    from app.kernel.application.alumnos.estadisticas import (
        ObtenerReporteRetrasosUseCase
    )
    
    uc = ObtenerReporteRetrasosUseCase(asis_alum_repo(db))
    return await uc.ejecutar(sede_id, fecha_inicio, fecha_fin, limite)


@router.get("/asistencia/faltas/reporte")
async def obtener_reporte_faltas(
    sede_id: int,
    fecha_inicio: date,
    fecha_fin: date,
    db: SessionDep,
    solo_sin_justificar: bool = False,
    limite: int = 100,
):
    """Obtener reporte de faltas.
    
    Lista todos los registros de ausencias (justificadas o no).
    Útil para seguimiento académico y alertas tempranas.
    """
    from app.kernel.application.alumnos.estadisticas import (
        ObtenerReporteFaltasUseCase
    )
    
    uc = ObtenerReporteFaltasUseCase(asis_alum_repo(db))
    return await uc.ejecutar(
        sede_id, 
        fecha_inicio, 
        fecha_fin, 
        solo_sin_justificar, 
        limite
    )

# app/interfaces/api/v1/cursos_extra.py

"""
Enrutador FastAPI para el módulo de Cursos Extra.
Gestiona todos los endpoints relacionados con cursos extracurriculares.
"""

from __future__ import annotations
from datetime import date, datetime
from decimal import Decimal
from typing import Annotated, Optional
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.session import get_session

# Repositorios
from app.infrastructure.db.repositories.cursos_extra.curso_extra_repo import CursoExtraRepository
from app.infrastructure.db.repositories.cursos_extra.inscripciones_curso_extra_repo import InscripcionCursoExtraRepository
from app.infrastructure.db.repositories.cursos_extra.alumno_externo_repo import AlumnoExternoRepository
from app.infrastructure.db.repositories.cursos_extra.balance_curso_extra_repo import BalanceCursoExtraRepository
from app.infrastructure.db.repositories.cursos_extra.pago_curso_extra_repo import PagoCursoExtraRepository
from app.infrastructure.db.repositories.cursos_extra.costo_curso_extra_repo import CostoCursoExtraRepository
from app.infrastructure.db.repositories.cursos_extra.categoria_costo_repo import CategoriaCostoCursoExtraRepository
from app.infrastructure.db.repositories.cursos_extra.ingreso_curso_extra_repo import IngresoCursoExtraRepository

# Casos de uso
from app.kernel.application.cursos_extra import (
    # Cursos Extra
    CrearCursoExtra,
    CrearCursoExtraDTO,
    ActualizarCursoExtra,
    ActualizarCursoExtraDTO,
    ListarCursosExtra,
    ListarCursosExtraDTO,
    ObtenerCursoExtra,
    GestionarEstadoCurso,
    # Inscripciones
    InscribirAlumnoInterno,
    InscribirAlumnoInternoDTO,
    InscribirAlumnoExterno,
    InscribirAlumnoExternoDTO,
    ListarInscripciones,
    ListarInscripcionesDTO,
    ObtenerInscripcion,
    GestionarEstadoInscripcion,
    # Alumnos Externos
    RegistrarAlumnoExterno,
    RegistrarAlumnoExternoDTO,
    ActualizarAlumnoExterno,
    ActualizarAlumnoExternoDTO,
    BuscarAlumnosExternos,
    BuscarAlumnosExternosDTO,
    ObtenerAlumnoExterno,
    # Balance
    CrearBalance,
    CrearBalanceDTO,
    ConsultarBalance,
    ListarBalances,
    ListarBalancesPendientesDTO,
    # Pagos
    RegistrarPago,
    RegistrarPagoDTO,
    ListarPagos,
    ListarPagosPorBalanceDTO,
    ConsultarPagosCurso,
    ConsultarPagosCursoDTO,
    # Costos
    RegistrarCosto,
    RegistrarCostoDTO,
    ActualizarCosto,
    ActualizarCostoDTO,
    EliminarCosto,
    ListarCostos,
    ListarCostosDTO,
    # Categorías de Costo
    CrearCategoriaCosto,
    CrearCategoriaCostoDTO,
    ActualizarCategoriaCosto,
    ActualizarCategoriaCostoDTO,
    GestionarEstadoCategoria,
    ListarCategoriasCosto,
    ListarCategoriasCostoDTO,
    # Reportes
    GenerarReporteFinanciero,
    GenerarReporteFinancieroDTO,
    ObtenerBalanceCurso,
    ConsultarEstadisticas,
)

router = APIRouter(prefix="/cursos-extra", tags=["Cursos Extra"])
SessionDep = Annotated[AsyncSession, Depends(get_session)]


# ============================================================================
# HELPERS - DEPENDENCY INJECTION
# ============================================================================

def curso_repo(db: AsyncSession) -> CursoExtraRepository:
    return CursoExtraRepository(db)

def inscripcion_repo(db: AsyncSession) -> InscripcionCursoExtraRepository:
    return InscripcionCursoExtraRepository(db)

def alumno_externo_repo(db: AsyncSession) -> AlumnoExternoRepository:
    return AlumnoExternoRepository(db)

def balance_repo(db: AsyncSession) -> BalanceCursoExtraRepository:
    return BalanceCursoExtraRepository(db)

def pago_repo(db: AsyncSession) -> PagoCursoExtraRepository:
    return PagoCursoExtraRepository(db)

def costo_repo(db: AsyncSession) -> CostoCursoExtraRepository:
    return CostoCursoExtraRepository(db)

def categoria_repo(db: AsyncSession) -> CategoriaCostoCursoExtraRepository:
    return CategoriaCostoCursoExtraRepository(db)

def ingreso_repo(db: AsyncSession) -> IngresoCursoExtraRepository:
    return IngresoCursoExtraRepository(db)


# ============================================================================
# CURSOS EXTRA
# ============================================================================

@router.post("", status_code=status.HTTP_201_CREATED)
async def crear_curso_extra(
    db: SessionDep,
    # payload: CrearCursoExtraRequest,
):
    """Crea un nuevo curso extra."""
    uc = CrearCursoExtra(curso_repo(db), ingreso_repo(db))
    # dto = CrearCursoExtraDTO(**payload.model_dump())
    # return await uc.execute(dto)
    return {"detail": "TODO implementar DTO creación curso extra"}


@router.get("/{curso_id}")
async def obtener_curso_extra(curso_id: int, db: SessionDep):
    """Obtiene un curso extra por su ID."""
    uc = ObtenerCursoExtra(curso_repo(db))
    return await uc.execute(curso_id)


@router.get("")
async def listar_cursos_extra(
    sede_id: int,
    db: SessionDep,
    activo: Optional[bool] = None,
    gestion: Optional[int] = None,
    solo_con_cupos: bool = False,
    limite: int = 100,
    offset: int = 0,
):
    """Lista cursos extra con filtros."""
    uc = ListarCursosExtra(curso_repo(db))
    dto = ListarCursosExtraDTO(
        sede_id=sede_id,
        activo=activo,
        gestion=gestion,
        solo_con_cupos=solo_con_cupos,
        limite=limite,
        offset=offset,
    )
    return await uc.execute(dto)


@router.put("/{curso_id}", status_code=status.HTTP_204_NO_CONTENT)
async def actualizar_curso_extra(
    curso_id: int,
    db: SessionDep,
    # payload: ActualizarCursoExtraRequest,
):
    """Actualiza un curso extra existente."""
    uc = ActualizarCursoExtra(curso_repo(db))
    # dto = ActualizarCursoExtraDTO(curso_id=curso_id, **payload.model_dump(exclude_unset=True))
    # await uc.execute(dto)
    return None


@router.put("/{curso_id}/activar", status_code=status.HTTP_204_NO_CONTENT)
async def activar_curso(curso_id: int, db: SessionDep):
    """Activa un curso extra."""
    uc = GestionarEstadoCurso(curso_repo(db))
    await uc.activar(curso_id)
    return None


@router.put("/{curso_id}/desactivar", status_code=status.HTTP_204_NO_CONTENT)
async def desactivar_curso(curso_id: int, db: SessionDep):
    """Desactiva un curso extra."""
    uc = GestionarEstadoCurso(curso_repo(db))
    await uc.desactivar(curso_id)
    return None


# ============================================================================
# INSCRIPCIONES
# ============================================================================

@router.post("/{curso_id}/inscripciones/interno", status_code=status.HTTP_201_CREATED)
async def inscribir_alumno_interno(
    curso_id: int,
    db: SessionDep,
    # payload: InscribirAlumnoInternoRequest,
):
    """Inscribe un alumno interno a un curso extra."""
    uc = InscribirAlumnoInterno(
        curso_repo(db),
        inscripcion_repo(db),
        balance_repo(db),
    )
    # dto = InscribirAlumnoInternoDTO(curso_extra_id=curso_id, **payload.model_dump())
    # return await uc.execute(dto)
    return {"detail": "TODO implementar DTO inscripción alumno interno"}


@router.post("/{curso_id}/inscripciones/externo", status_code=status.HTTP_201_CREATED)
async def inscribir_alumno_externo(
    curso_id: int,
    db: SessionDep,
    # payload: InscribirAlumnoExternoRequest,
):
    """Inscribe un alumno externo a un curso extra."""
    uc = InscribirAlumnoExterno(
        curso_repo(db),
        inscripcion_repo(db),
        balance_repo(db),
        alumno_externo_repo(db),
    )
    # dto = InscribirAlumnoExternoDTO(curso_extra_id=curso_id, **payload.model_dump())
    # return await uc.execute(dto)
    return {"detail": "TODO implementar DTO inscripción alumno externo"}


@router.get("/{curso_id}/inscripciones")
async def listar_inscripciones(
    curso_id: int,
    db: SessionDep,
    estado: Optional[str] = None,
    limite: int = 100,
    offset: int = 0,
):
    """Lista inscripciones de un curso."""
    uc = ListarInscripciones(inscripcion_repo(db))
    from app.kernel.domain.cursos_extra import EstadoInscripcionCursoExtra
    estado_enum = EstadoInscripcionCursoExtra(estado) if estado else None
    dto = ListarInscripcionesDTO(
        curso_id=curso_id,
        estado=estado_enum,
        limite=limite,
        offset=offset,
    )
    return await uc.execute(dto)


@router.get("/inscripciones/{inscripcion_id}")
async def obtener_inscripcion(inscripcion_id: int, db: SessionDep):
    """Obtiene una inscripción por su ID."""
    uc = ObtenerInscripcion(inscripcion_repo(db))
    return await uc.execute(inscripcion_id)


@router.put("/inscripciones/{inscripcion_id}/completar", status_code=status.HTTP_204_NO_CONTENT)
async def completar_inscripcion(inscripcion_id: int, db: SessionDep):
    """Marca una inscripción como completada."""
    uc = GestionarEstadoInscripcion(inscripcion_repo(db), curso_repo(db))
    await uc.completar(inscripcion_id)
    return None


@router.put("/inscripciones/{inscripcion_id}/retirar", status_code=status.HTTP_204_NO_CONTENT)
async def retirar_inscripcion(inscripcion_id: int, db: SessionDep):
    """Retira un alumno del curso."""
    uc = GestionarEstadoInscripcion(inscripcion_repo(db), curso_repo(db))
    await uc.retirar(inscripcion_id)
    return None


@router.put("/inscripciones/{inscripcion_id}/reactivar", status_code=status.HTTP_204_NO_CONTENT)
async def reactivar_inscripcion(inscripcion_id: int, db: SessionDep):
    """Reactiva una inscripción retirada."""
    uc = GestionarEstadoInscripcion(inscripcion_repo(db), curso_repo(db))
    await uc.reactivar(inscripcion_id)
    return None


# ============================================================================
# ALUMNOS EXTERNOS
# ============================================================================

@router.post("/alumnos-externos", status_code=status.HTTP_201_CREATED)
async def registrar_alumno_externo(
    db: SessionDep,
    # payload: RegistrarAlumnoExternoRequest,
):
    """Registra un alumno externo en el sistema."""
    uc = RegistrarAlumnoExterno(alumno_externo_repo(db))
    # dto = RegistrarAlumnoExternoDTO(**payload.model_dump())
    # return await uc.execute(dto)
    return {"detail": "TODO implementar DTO registro alumno externo"}


@router.get("/alumnos-externos/{alumno_id}")
async def obtener_alumno_externo(alumno_id: int, db: SessionDep):
    """Obtiene un alumno externo por su ID."""
    uc = ObtenerAlumnoExterno(alumno_externo_repo(db))
    return await uc.execute(alumno_id)


@router.get("/alumnos-externos")
async def buscar_alumnos_externos(
    termino: str,
    db: SessionDep,
    tipo_busqueda: str = Query("nombre", regex="^(nombre|celular)$"),
    sede_id: Optional[int] = None,
    limite: int = 20,
):
    """Busca alumnos externos por nombre o celular del tutor."""
    uc = BuscarAlumnosExternos(alumno_externo_repo(db))
    dto = BuscarAlumnosExternosDTO(
        termino_busqueda=termino,
        tipo_busqueda=tipo_busqueda,
        sede_id=sede_id,
        limite=limite,
    )
    return await uc.execute(dto)


@router.put("/alumnos-externos/{alumno_id}", status_code=status.HTTP_204_NO_CONTENT)
async def actualizar_alumno_externo(
    alumno_id: int,
    db: SessionDep,
    # payload: ActualizarAlumnoExternoRequest,
):
    """Actualiza datos de un alumno externo."""
    uc = ActualizarAlumnoExterno(alumno_externo_repo(db))
    # dto = ActualizarAlumnoExternoDTO(alumno_id=alumno_id, **payload.model_dump(exclude_unset=True))
    # await uc.execute(dto)
    return None


# ============================================================================
# BALANCE
# ============================================================================

@router.post("/balance", status_code=status.HTTP_201_CREATED)
async def crear_balance(
    db: SessionDep,
    # payload: CrearBalanceRequest,
):
    """Crea un balance para una inscripción (caso especial)."""
    uc = CrearBalance(balance_repo(db), inscripcion_repo(db))
    # dto = CrearBalanceDTO(**payload.model_dump())
    # return await uc.execute(dto)
    return {"detail": "TODO implementar DTO creación balance"}


@router.get("/balance/{balance_id}")
async def consultar_balance_por_id(balance_id: int, db: SessionDep):
    """Consulta un balance por su ID."""
    uc = ConsultarBalance(balance_repo(db))
    return await uc.por_id(balance_id)


@router.get("/inscripciones/{inscripcion_id}/balance")
async def consultar_balance_por_inscripcion(inscripcion_id: int, db: SessionDep):
    """Consulta el balance de una inscripción."""
    uc = ConsultarBalance(balance_repo(db))
    return await uc.por_inscripcion(inscripcion_id)


@router.get("/{curso_id}/balances/pendientes")
async def listar_balances_pendientes(curso_id: int, db: SessionDep):
    """Lista balances pendientes o parciales de un curso."""
    uc = ListarBalances(balance_repo(db))
    dto = ListarBalancesPendientesDTO(curso_id=curso_id)
    return await uc.pendientes_por_curso(dto)


# ============================================================================
# PAGOS
# ============================================================================

@router.post("/pagos", status_code=status.HTTP_201_CREATED)
async def registrar_pago(
    db: SessionDep,
    # payload: RegistrarPagoRequest,
):
    """Registra un pago para una inscripción."""
    uc = RegistrarPago(
        pago_repo(db),
        balance_repo(db),
        ingreso_repo(db),
        inscripcion_repo(db),
    )
    # dto = RegistrarPagoDTO(**payload.model_dump())
    # return await uc.execute(dto)
    return {"detail": "TODO implementar DTO registro pago"}


@router.get("/balance/{balance_id}/pagos")
async def listar_pagos_por_balance(balance_id: int, db: SessionDep):
    """Lista todos los pagos de un balance."""
    uc = ListarPagos(pago_repo(db))
    dto = ListarPagosPorBalanceDTO(balance_id=balance_id)
    return await uc.por_balance(dto)


@router.get("/{curso_id}/pagos")
async def consultar_pagos_curso(
    curso_id: int,
    db: SessionDep,
    fecha_desde: Optional[date] = None,
    fecha_hasta: Optional[date] = None,
    limite: int = 100,
    offset: int = 0,
):
    """Lista pagos de un curso con filtros de fecha."""
    uc = ConsultarPagosCurso(pago_repo(db))
    dto = ConsultarPagosCursoDTO(
        curso_id=curso_id,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
        limite=limite,
        offset=offset,
    )
    return await uc.listar(dto)


@router.get("/{curso_id}/pagos/total")
async def calcular_total_pagos_curso(
    curso_id: int,
    db: SessionDep,
    fecha_desde: Optional[date] = None,
    fecha_hasta: Optional[date] = None,
):
    """Calcula el total de pagos de un curso."""
    uc = ConsultarPagosCurso(pago_repo(db))
    dto = ConsultarPagosCursoDTO(
        curso_id=curso_id,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
    )
    return await uc.calcular_total(dto)


# ============================================================================
# COSTOS
# ============================================================================

@router.post("/{curso_id}/costos", status_code=status.HTTP_201_CREATED)
async def registrar_costo(
    curso_id: int,
    db: SessionDep,
    # payload: RegistrarCostoRequest,
):
    """Registra un costo/gasto de un curso extra."""
    uc = RegistrarCosto(
        costo_repo(db),
        categoria_repo(db),
        ingreso_repo(db),
        curso_repo(db),
    )
    # dto = RegistrarCostoDTO(curso_extra_id=curso_id, **payload.model_dump())
    # return await uc.execute(dto)
    return {"detail": "TODO implementar DTO registro costo"}


@router.get("/{curso_id}/costos")
async def listar_costos(
    curso_id: int,
    db: SessionDep,
    fecha_desde: Optional[datetime] = None,
    fecha_hasta: Optional[datetime] = None,
    limite: int = 100,
    offset: int = 0,
):
    """Lista costos de un curso."""
    uc = ListarCostos(costo_repo(db))
    dto = ListarCostosDTO(
        curso_id=curso_id,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
        limite=limite,
        offset=offset,
    )
    return await uc.execute(dto)


@router.put("/costos/{costo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def actualizar_costo(
    costo_id: int,
    db: SessionDep,
    # payload: ActualizarCostoRequest,
):
    """Actualiza un costo existente."""
    uc = ActualizarCosto(costo_repo(db), ingreso_repo(db))
    # dto = ActualizarCostoDTO(costo_id=costo_id, **payload.model_dump(exclude_unset=True))
    # await uc.execute(dto)
    return None


@router.delete("/costos/{costo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_costo(costo_id: int, db: SessionDep):
    """Elimina un costo."""
    uc = EliminarCosto(costo_repo(db), ingreso_repo(db))
    await uc.execute(costo_id)
    return None


# ============================================================================
# CATEGORÍAS DE COSTO
# ============================================================================

@router.post("/{curso_id}/categorias-costo", status_code=status.HTTP_201_CREATED)
async def crear_categoria_costo(
    curso_id: int,
    db: SessionDep,
    # payload: CrearCategoriaCostoRequest,
):
    """Crea una categoría dinámica de costo para un curso."""
    uc = CrearCategoriaCosto(categoria_repo(db), curso_repo(db))
    # dto = CrearCategoriaCostoDTO(curso_extra_id=curso_id, **payload.model_dump())
    # return await uc.execute(dto)
    return {"detail": "TODO implementar DTO creación categoría costo"}


@router.get("/{curso_id}/categorias-costo")
async def listar_categorias_costo(
    curso_id: int,
    db: SessionDep,
    activo: Optional[bool] = None,
):
    """Lista categorías de costo de un curso."""
    uc = ListarCategoriasCosto(categoria_repo(db))
    dto = ListarCategoriasCostoDTO(curso_id=curso_id, activo=activo)
    return await uc.execute(dto)


@router.put("/categorias-costo/{categoria_id}", status_code=status.HTTP_204_NO_CONTENT)
async def actualizar_categoria_costo(
    categoria_id: int,
    db: SessionDep,
    # payload: ActualizarCategoriaCostoRequest,
):
    """Actualiza una categoría de costo."""
    uc = ActualizarCategoriaCosto(categoria_repo(db))
    # dto = ActualizarCategoriaCostoDTO(categoria_id=categoria_id, **payload.model_dump(exclude_unset=True))
    # await uc.execute(dto)
    return None


@router.put("/categorias-costo/{categoria_id}/activar", status_code=status.HTTP_204_NO_CONTENT)
async def activar_categoria(categoria_id: int, db: SessionDep):
    """Activa una categoría de costo."""
    uc = GestionarEstadoCategoria(categoria_repo(db))
    await uc.activar(categoria_id)
    return None


@router.put("/categorias-costo/{categoria_id}/desactivar", status_code=status.HTTP_204_NO_CONTENT)
async def desactivar_categoria(categoria_id: int, db: SessionDep):
    """Desactiva una categoría de costo."""
    uc = GestionarEstadoCategoria(categoria_repo(db))
    await uc.desactivar(categoria_id)
    return None


# ============================================================================
# REPORTES Y ESTADÍSTICAS
# ============================================================================

@router.get("/{curso_id}/reporte-financiero")
async def generar_reporte_financiero(
    curso_id: int,
    db: SessionDep,
    fecha_desde: Optional[date] = None,
    fecha_hasta: Optional[date] = None,
):
    """Genera un reporte financiero completo del curso."""
    uc = GenerarReporteFinanciero(
        curso_repo(db),
        pago_repo(db),
        costo_repo(db),
        balance_repo(db),
        ingreso_repo(db),
    )
    dto = GenerarReporteFinancieroDTO(
        curso_id=curso_id,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
    )
    return await uc.execute(dto)


@router.get("/{curso_id}/balance-consolidado")
async def obtener_balance_consolidado(curso_id: int, db: SessionDep):
    """Obtiene el balance consolidado de un curso."""
    uc = ObtenerBalanceCurso(ingreso_repo(db), curso_repo(db))
    return await uc.execute(curso_id)


@router.get("/{curso_id}/estadisticas")
async def consultar_estadisticas(curso_id: int, db: SessionDep):
    """Consulta estadísticas de inscripciones del curso."""
    uc = ConsultarEstadisticas(curso_repo(db), inscripcion_repo(db))
    return await uc.execute(curso_id)

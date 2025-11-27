# app/interfaces/api/v1/finanzas.py
from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field, ConfigDict

# Domain reexports (en tu dominio ya están)
from app.kernel.domain.finanzas import TipoMovimiento, MetodoPago  # enums
# Casos de uso (importa según tu estructura de application/)
from app.kernel.application.finanzas.categoria_pago.crear_categoria_pago import (
    CrearCategoriaPagoUseCase, CrearCategoriaPagoCommand,
)
from app.kernel.application.finanzas.categoria_pago.listar_categorias_pago import (
    ListarCategoriasPagoUseCase, ListarCategoriasPagoQuery,
)
from app.kernel.application.finanzas.categoria_pago.actualizar_categoria_pago import (
    ActualizarCategoriaPagoUseCase, ActualizarCategoriaPagoCommand,
)
from app.kernel.application.finanzas.categoria_egreso.crear_categoria_egreso import (
    CrearCategoriaEgresoUseCase, CrearCategoriaEgresoCommand,
)
from app.kernel.application.finanzas.categoria_egreso.listar_categorias_egreso import (
    ListarCategoriasEgresoUseCase, ListarCategoriasEgresoQuery,
)
from app.kernel.application.finanzas.categoria_egreso.actualizar_categoria_egreso import (
    ActualizarCategoriaEgresoUseCase, ActualizarCategoriaEgresoCommand,
)
from app.kernel.application.finanzas.libro_de_caja.registrar_ingreso_caja import (
    RegistrarIngresoCajaUseCase, RegistrarIngresoCommand,
)
from app.kernel.application.finanzas.egresos.registrar_egreso import (
    RegistrarEgresoUseCase, RegistrarEgresoCommand,
)
from app.kernel.application.finanzas.libro_de_caja.listar_movimientos_caja import (
    ListarMovimientosCajaUseCase, ListarMovimientosCajaQuery,
)
from app.kernel.application.finanzas.libro_de_caja.obtener_saldo_sede import (
    ObtenerSaldoSedeUseCase, ObtenerSaldoSedeQuery,
)
from app.kernel.application.finanzas.libro_de_caja.obtener_totales_periodo import (
    ObtenerTotalesPeriodoUseCase, ObtenerTotalesPeriodoQuery,
)
from app.kernel.application.finanzas.pagos.registrar_pago import (
    RegistrarPagoUseCase, RegistrarPagoCommand,
)
from app.kernel.application.finanzas.pagos.listar_pagos import (
    ListarPagosUseCase, ListarPagosQuery, PagoListadoDTO,
)
from app.kernel.application.finanzas.pagos.anular_pago import (
    AnularPagoUseCase, AnularPagoCommand,
)
from app.kernel.application.finanzas.egresos.listar_egresos import (
    ListarEgresosUseCase, ListarEgresosQuery,
)
from app.kernel.application.finanzas.egresos.anular_egreso import (
    AnularEgresoUseCase, AnularEgresoCommand,
)
from app.kernel.application.finanzas.arqueo.generar_arqueo_mensual import (
    GenerarArqueoMensualUseCase, GenerarArqueoMensualCommand,
)
from app.kernel.application.finanzas.arqueo.listar_arqueos import (
    ListarArqueosUseCase, ListarArqueosQuery,
)
from app.kernel.application.finanzas.arqueo.recalcular_arqueo import (
    RecalcularArqueoUseCase, RecalcularArqueoCommand,
)

# Infra: sesiones y repos (ajusta rutas concretas a tus factories)
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.db.session import get_session  # define tu dependency
from app.infrastructure.db.repositories.finanzas import (
    CategoriasPagoRepository,
    LibroCajaRepository,
    PagosRepository,
    ArqueosRepository,
)  # agrega los demás repos concretos

router = APIRouter(prefix="/api/v1/finanzas", tags=["Finanzas"])

# ==== Seguridad / RBAC (stubs) ====
class CurrentUser(BaseModel):
    id: int
    sede_id: int
    roles: list[str]

async def get_current_user() -> CurrentUser:
    # Implementa con tu JWT/session manager
    return CurrentUser(id=1, sede_id=1, roles=["admin"])

def require_role(user: CurrentUser, roles: list[str]):
    if not any(r in user.roles for r in roles):
        raise HTTPException(status_code=403, detail="No autorizado")


# ==== DTOs ====
class CategoriaBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    nombre: str = Field(..., max_length=100)
    descripcion: Optional[str] = None

class CategoriaPagoCreate(CategoriaBase):
    monto_base: Optional[Decimal] = None

class CategoriaUpdate(BaseModel):
    nombre: Optional[str] = Field(None, max_length=100)
    descripcion: Optional[str] = None
    activa: Optional[bool] = None

class IngresoCreate(BaseModel):
    sede_id: int
    categoria_pago_id: int
    monto: Decimal
    fecha: date
    concepto: Optional[str] = None
    referencia: Optional[str] = None
    pago_id: Optional[int] = None

class EgresoCreate(BaseModel):
    sede_id: int
    categoria_egreso_id: int
    monto: Decimal
    fecha: date
    concepto: Optional[str] = None
    referencia: Optional[str] = None

class PagoCreate(BaseModel):
    sede_id: int
    categoria_pago_id: int
    monto: Decimal
    metodo: MetodoPago
    comprobante_id: int
    fecha: date
    concepto: Optional[str] = None
    referencia: Optional[str] = None
    monto_esperado: Optional[Decimal] = None
    nino_id: Optional[int] = None
    curso_extra_id: Optional[int] = None
    plan_cuota_id: Optional[int] = None

class PeriodoQuery(BaseModel):
    sede_id: int
    fecha_inicio: date
    fecha_fin: date
    tipo: Optional[TipoMovimiento] = None

router = APIRouter(prefix="/api/v1/finanzas", tags=["Finanzas"])
# ==== Categorías de pago ====
@router.post("/ingresos/categorias")
async def crear_categoria_pago(
    body: CategoriaPagoCreate,
    user: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    require_role(user, ["admin", "contabilidad"])
    use = CrearCategoriaPagoUseCase(CategoriasPagoRepository(session))
    cmd = CrearCategoriaPagoCommand(
        sede_id=user.sede_id,
        nombre=body.nombre,
        descripcion=body.descripcion,
        monto_base=body.monto_base,
        usuario_id=user.id,
    )
    return await use.execute(cmd)

@router.get("/ingresos/categorias")
async def listar_categorias_pago(
    solo_activas: bool = True,
    user: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    use = ListarCategoriasPagoUseCase(CategoriasPagoRepository(session))
    q = ListarCategoriasPagoQuery(sede_id=user.sede_id, solo_activas=solo_activas)
    return await use.execute(q)

@router.put("/ingresos/categorias/{categoria_id}")
async def actualizar_categoria_pago(
    categoria_id: int,
    body: CategoriaUpdate,
    user: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    require_role(user, ["admin", "contabilidad"])
    use = ActualizarCategoriaPagoUseCase(CategoriasPagoRepository(session))
    cmd = ActualizarCategoriaPagoCommand(
        categoria_id=categoria_id,
        nombre=body.nombre,
        descripcion=body.descripcion,
        activa=body.activa,
        usuario_id=user.id,
    )
    return await use.execute(cmd)

# ==== Categorías de egreso ====
from app.infrastructure.db.repositories.finanzas.categorias_egreso_repo import CategoriaEgresoRepository  # asegura este repo

@router.post("/egresos/categorias")
async def crear_categoria_egreso(
    body: CategoriaBase,
    user: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    require_role(user, ["admin", "contabilidad"])
    use = CrearCategoriaEgresoUseCase(CategoriaEgresoRepository(session))
    cmd = CrearCategoriaEgresoCommand(
        sede_id=user.sede_id,
        nombre=body.nombre,
        descripcion=body.descripcion,
        usuario_id=user.id,
    )
    return await use.execute(cmd)

@router.get("/egresos/categorias")
async def listar_categorias_egreso(
    solo_activas: bool = True,
    user: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    use = ListarCategoriasEgresoUseCase(CategoriaEgresoRepository(session))
    q = ListarCategoriasEgresoQuery(sede_id=user.sede_id, solo_activas=solo_activas)
    return await use.execute(q)

@router.put("/egresos/categorias/{categoria_id}")
async def actualizar_categoria_egreso(
    categoria_id: int,
    body: CategoriaUpdate,
    user: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    require_role(user, ["admin", "contabilidad"])
    use = ActualizarCategoriaEgresoUseCase(CategoriaEgresoRepository(session))
    cmd = ActualizarCategoriaEgresoCommand(
        categoria_id=categoria_id,
        nombre=body.nombre,
        descripcion=body.descripcion,
        activa=body.activa,
        usuario_id=user.id,
    )
    return await use.execute(cmd)

# ==== Libro de Caja: ingresos/egresos ====
@router.post("/ingresos")
async def registrar_ingreso(
    body: IngresoCreate,
    user: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    require_role(user, ["admin", "contabilidad"])
    use = RegistrarIngresoCajaUseCase(
        libro_repo=LibroCajaRepository(session),
        categoria_repo=CategoriasPagoRepository(session),
        pago_repo=PagosRepository(session),
    )
    cmd = RegistrarIngresoCommand(
        sede_id=user.sede_id,
        categoria_pago_id=body.categoria_pago_id,
        monto=body.monto,
        fecha=body.fecha,
        concepto=body.concepto,
        referencia=body.referencia,
        pago_id=body.pago_id,
        usuario_registro_id=user.id,
    )
    return await use.execute(cmd)

@router.post("/egresos")
async def registrar_egreso(
    body: EgresoCreate,
    user: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    require_role(user, ["admin", "contabilidad"])
    use = RegistrarEgresoUseCase(
        libro_repo=LibroCajaRepository(session),
        categoria_repo=CategoriaEgresoRepository(session),
    )
    cmd = RegistrarEgresoCommand(
        sede_id=user.sede_id,
        categoria_egreso_id=body.categoria_egreso_id,
        monto=body.monto,
        fecha=body.fecha,
        concepto=body.concepto,
        referencia=body.referencia,
        usuario_registro_id=user.id,
    )
    return await use.execute(cmd)

@router.get("/libro")
async def listar_libro(
    fecha_inicio: date = Query(...),
    fecha_fin: date = Query(...),
    tipo: Optional[TipoMovimiento] = Query(None),
    user: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    use = ListarMovimientosCajaUseCase(LibroCajaRepository(session))
    q = ListarMovimientosCajaQuery(
        sede_id=user.sede_id, fecha_inicio=fecha_inicio, fecha_fin=fecha_fin, tipo=tipo
    )
    return await use.execute(q)

@router.get("/saldo")
async def obtener_saldo(
    user: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    use = ObtenerSaldoSedeUseCase(LibroCajaRepository(session))
    return {"sede_id": user.sede_id, "saldo": await use.execute(ObtenerSaldoSedeQuery(user.sede_id))}

@router.get("/totales")
async def obtener_totales(
    fecha_inicio: date = Query(...),
    fecha_fin: date = Query(...),
    user: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    use = ObtenerTotalesPeriodoUseCase(LibroCajaRepository(session))
    ing, egr, saldo = await use.execute(
        ObtenerTotalesPeriodoQuery(sede_id=user.sede_id, fecha_inicio=fecha_inicio, fecha_fin=fecha_fin)
    )
    return {"ingresos": ing, "egresos": egr, "saldo_final": saldo}

# ==== Pagos ====
from app.infrastructure.db.repositories.finanzas.comprobantes_repo import ComprobantesRepository  # asegura este repo

@router.post("/pagos")
async def registrar_pago(
    body: PagoCreate,
    user: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    require_role(user, ["admin", "caja", "contabilidad"])
    use = RegistrarPagoUseCase(
        pago_repo=PagosRepository(session),
        comp_repo=ComprobantesRepository(session),
        categoria_repo=CategoriasPagoRepository(session),
        libro_repo=LibroCajaRepository(session),
    )
    cmd = RegistrarPagoCommand(
        sede_id=user.sede_id,
        categoria_pago_id=body.categoria_pago_id,
        monto=body.monto,
        metodo=body.metodo,
        comprobante_id=body.comprobante_id,
        creado_por_usuario_id=user.id,
        fecha=body.fecha,
        concepto=body.concepto,
        referencia=body.referencia,
        monto_esperado=body.monto_esperado,
        nino_id=body.nino_id,
        curso_extra_id=body.curso_extra_id,
        plan_cuota_id=body.plan_cuota_id,
    )
    return await use.execute(cmd)

@router.get("/pagos")
async def listar_pagos(
    fecha_inicio: Optional[date] = None,
    fecha_fin: Optional[date] = None,
    categoria_id: Optional[int] = None,
    metodo: Optional[MetodoPago] = None,
    limit: int = 50,
    offset: int = 0,
    user: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    use = ListarPagosUseCase(
        pago_repo=PagosRepository(session),
        libro_repo=LibroCajaRepository(session)
    )
    q = ListarPagosQuery(
        sede_id=user.sede_id,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        categoria_id=categoria_id,
        metodo=metodo,
        limit=limit,
        offset=offset,
    )
    dtos: List[PagoListadoDTO] = await use.execute(q)
    return [
        {
            "id": dto.pago.id,
            "monto": dto.pago.monto,
            "metodo": dto.pago.metodo,
            "categoria_id": dto.pago.categoria_id,
            "comprobante_id": dto.pago.comprobante_id,
            "anulado": dto.anulado,
        }
        for dto in dtos
    ]

@router.post("/pagos/{pago_id}/anular")
async def anular_pago(
    pago_id: int,
    fecha: date,
    categoria_egreso_id: Optional[int] = None,
    referencia: Optional[str] = None,
    concepto: Optional[str] = None,
    user: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    require_role(user, ["admin", "contabilidad"])
    use = AnularPagoUseCase(
        pago_repo=PagosRepository(session),
        libro_repo=LibroCajaRepository(session)
    )
    cmd = AnularPagoCommand(
        pago_id=pago_id,
        sede_id=user.sede_id,
        fecha=fecha,
        usuario_registro_id=user.id,
        referencia=referencia,
        concepto=concepto,
        categoria_egreso_id=categoria_egreso_id,
    )
    return await use.execute(cmd)

# ==== Egresos: listado y reversa ====
@router.get("/egresos")
async def listar_egresos(
    fecha_inicio: date = Query(...),
    fecha_fin: date = Query(...),
    categoria_egreso_id: Optional[int] = None,
    user: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    use = ListarEgresosUseCase(LibroCajaRepository(session))
    q = ListarEgresosQuery(
        sede_id=user.sede_id,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        categoria_egreso_id=categoria_egreso_id,
    )
    return await use.execute(q)

@router.post("/egresos/{movimiento_id}/anular")
async def anular_egreso(
    movimiento_id: int,
    fecha: date,
    categoria_pago_id: Optional[int] = None,
    referencia: Optional[str] = None,
    concepto: Optional[str] = None,
    user: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    require_role(user, ["admin", "contabilidad"])
    use = AnularEgresoUseCase(LibroCajaRepository(session))
    cmd = AnularEgresoCommand(
        movimiento_id=movimiento_id,
        sede_id=user.sede_id,
        fecha=fecha,
        usuario_registro_id=user.id,
        referencia=referencia,
        concepto=concepto,
        categoria_pago_id=categoria_pago_id,
    )
    return await use.execute(cmd)

# ==== Arqueos ====
@router.post("/arqueos/generar")
async def generar_arqueo(
    anio: int,
    mes: int,
    observaciones: Optional[str] = None,
    user: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    require_role(user, ["admin", "contabilidad"])
    use = GenerarArqueoMensualUseCase(
        arqueo_repo=ArqueosRepository(session),
        libro_repo=LibroCajaRepository(session),
    )
    cmd = GenerarArqueoMensualCommand(
        sede_id=user.sede_id, anio=anio, mes=mes, observaciones=observaciones
    )
    return await use.execute(cmd)

@router.get("/arqueos")
async def listar_arqueos(
    limite: int = 24,
    user: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    use = ListarArqueosUseCase(ArqueosRepository(session))
    q = ListarArqueosQuery(sede_id=user.sede_id, limite=limite)
    return await use.execute(q)

@router.post("/arqueos/{arqueo_id}/recalcular")
async def recalcular_arqueo(
    arqueo_id: int,
    user: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    require_role(user, ["admin", "contabilidad"])
    use = RecalcularArqueoUseCase(
        arqueo_repo=ArqueosRepository(session),
        libro_repo=LibroCajaRepository(session),
    )
    cmd = RecalcularArqueoCommand(arqueo_id=arqueo_id)
    return await use.execute(cmd)

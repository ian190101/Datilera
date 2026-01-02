"""
Router de Finanzas - Sistema Datilera
Agrupa todos los endpoints relacionados con operaciones financieras:
- Pagos, Planes de Pago, Prorrateo
- Egresos, Descuentos
- Arqueos, Categorías (Pago/Egreso)
- Conciliaciones, Dashboard
- Estado de Cuenta, Libro de Caja
"""

from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.session import get_session

from app.kernel.domain.seguridad.user_entidad import Usuario
from app.kernel.domain.finanzas.errors import (
    PagoNoEncontradoError,
    EgresoNoEncontradoError,
    PlanPagoNoEncontradoError,
    CategoriaPagoNoEncontradaError,
    CategoriaEgresoNoEncontradaError,
    ArqueoNoEncontradoError,
    ConciliacionError,
    DescuentoNoEncontradoError,
    EstadoCuentaError,
)

# ========================================
# IMPORTS - PAGOS
# ========================================
from app.kernel.application.finanzas.pagos.registrar_pago import RegistrarPagoUC
from app.kernel.application.finanzas.pagos.listar_pagos import ListarPagosUC
from app.kernel.application.finanzas.pagos.anular_pago import AnularPagoUC

# ========================================
# IMPORTS - PLANES DE PAGO
# ========================================
from app.kernel.application.finanzas.planes_pago.crear_plan_pago import CrearPlanPagoCU
from app.kernel.application.finanzas.planes_pago.obtener_plan_pago_alumno import ObtenerPlanPagoAlumnoCU
from app.kernel.application.finanzas.planes_pago.actualizar_cuotas_plan import ActualizarCuotasPlanCU
from app.kernel.application.finanzas.planes_pago.obtener_tabla_amortizacion import ObtenerTablaAmortizacionCU

# ========================================
# IMPORTS - PRORRATEO
# ========================================
from app.kernel.application.finanzas.prorrateo.calcular_prorrateo import CalcularProrrateoCU

# ========================================
# IMPORTS - EGRESOS
# ========================================
from app.kernel.application.finanzas.egresos.registrar_egreso import RegistrarEgresoUC
from app.kernel.application.finanzas.egresos.listar_egresos import ListarEgresosUC
from app.kernel.application.finanzas.egresos.anular_egreso import AnularEgresoUC

# ========================================
# IMPORTS - DESCUENTOS
# ========================================
from app.kernel.application.finanzas.descuentos.aplicar_descuento import AplicarDescuentoCU
from app.kernel.application.finanzas.descuentos.calcular_descuento_disponible import CalcularDescuentoDisponibleCU

# ========================================
# IMPORTS - ARQUEO
# ========================================
from app.kernel.application.finanzas.arqueo.generar_arqueo_mensual import GenerarArqueoMensualUseCase
from app.kernel.application.finanzas.arqueo.listar_arqueos import ListarArqueosUseCase
from app.kernel.application.finanzas.arqueo.recalcular_arqueo import RecalcularArqueoUseCase

# ========================================
# IMPORTS - CATEGORÍA EGRESO
# ========================================
from app.kernel.application.finanzas.categoria_egreso.crear_categoria_egreso import CrearCategoriaEgresoUseCase
from app.kernel.application.finanzas.categoria_egreso.listar_categorias_egreso import ListarCategoriasEgresoUseCase
from app.kernel.application.finanzas.categoria_egreso.actualizar_categoria_egreso import ActualizarCategoriaEgresoUseCase

# ========================================
# IMPORTS - CATEGORÍA PAGO
# ========================================
from app.kernel.application.finanzas.categoria_pago.crear_categoria_pago import CrearCategoriaPagoUseCase
from app.kernel.application.finanzas.categoria_pago.listar_categorias_pago import ListarCategoriasPagoUseCase
from app.kernel.application.finanzas.categoria_pago.actualizar_categoria_pago import ActualizarCategoriaPagoUseCase

# ========================================
# IMPORTS - CONCILIACIONES
# ========================================
from app.kernel.application.finanzas.conciliaciones.marcar_pago_depositado import MarcarPagoDepositadoCU
from app.kernel.application.finanzas.conciliaciones.marcar_pago_transferido import MarcarPagoTransferidoCU
from app.kernel.application.finanzas.conciliaciones.listar_pendientes_transferir import ListarPendientesTransferirCU
from app.kernel.application.finanzas.conciliaciones.verificar_conciliacion import VerificarConciliacionCU
from app.kernel.application.finanzas.conciliaciones.obtener_historial_transferencias import ObtenerHistorialTransferenciasCU

# ========================================
# IMPORTS - DASHBOARD
# ========================================
from app.kernel.application.finanzas.dashboard.obtener_dashboard_sede import ObtenerDashboardSedeCU
from app.kernel.application.finanzas.dashboard.obtener_asistencia_promedio import ObtenerAsistenciaPromedioCU
from app.kernel.application.finanzas.dashboard.obtener_nuevos_inscritos_por_mes import ObtenerNuevosInscritosPorMesCU
from app.kernel.application.finanzas.dashboard.obtener_inscritos_por_mes import ObtenerInscritosPorMesCU
from app.kernel.application.finanzas.dashboard.obtener_ingresos_egresos_mes import ObtenerIngresosEgresosMesCU
from app.kernel.application.finanzas.dashboard.obtener_ocupacion_paralelos import ObtenerOcupacionParalelosCU
from app.kernel.application.finanzas.dashboard.obtener_pagos_por_categoria import ObtenerPagosPorCategoriaCU
from app.kernel.application.finanzas.dashboard.obtener_rentabilidad_sede import ObtenerRentabilidadSedeCU
from app.kernel.application.finanzas.dashboard.obtener_reporte_deudores import ObtenerReporteDeudoresCU

# ========================================
# IMPORTS - ESTADO DE CUENTA
# ========================================
from app.kernel.application.finanzas.estado_cuenta.obtener_estado_cuenta_detallado import ObtenerEstadoCuentaDetalladoCU
from app.kernel.application.finanzas.estado_cuenta.listar_alumnos_morosos import ListarAlumnosMorososCU
from app.kernel.application.finanzas.estado_cuenta.enviar_recordatorio_pago import EnviarRecordatorioPagoCU
from app.kernel.application.finanzas.estado_cuenta.verificar_alumno_moroso import VerificarAlumnoMorosoCU

# ========================================
# IMPORTS - LIBRO CAJA
# ========================================
from app.kernel.application.finanzas.libro_de_caja.registrar_ingreso_caja import RegistrarIngresoCajaUseCase
from app.kernel.application.finanzas.libro_de_caja.registrar_egreso_caja import RegistrarEgresoCajaUseCase
from app.kernel.application.finanzas.libro_de_caja.listar_movimientos_caja import ListarMovimientosCajaUseCase
from app.kernel.application.finanzas.libro_de_caja.obtener_saldo_sede import ObtenerSaldoSedeUseCase
from app.kernel.application.finanzas.libro_de_caja.obtener_totales_periodo import ObtenerTotalesPeriodoUseCase

# ========================================
# REPOSITORIOS
# ========================================
from app.infrastructure.db.repositories.finanzas.pagos_repo import PagosRepository
from app.infrastructure.db.repositories.finanzas.planes_pago_repo import PlanesPagoRepository
from app.infrastructure.db.repositories.finanzas.cuotas_plan_pago_repo import CuotasPlanPagoRepository
from app.infrastructure.db.repositories.finanzas.prorrateos_repo import ProrrateosRepository
from app.infrastructure.db.repositories.finanzas.egresos_repo import EgresosRepository
from app.infrastructure.db.repositories.finanzas.descuentos_repo import DescuentosRepository
from app.infrastructure.db.repositories.finanzas.arqueos_repo import ArqueosRepository
from app.infrastructure.db.repositories.finanzas.categorias_egreso_repo import CategoriaEgresoRepository
from app.infrastructure.db.repositories.finanzas.categorias_pago_repo import CategoriasPagoRepository
from app.infrastructure.db.repositories.finanzas.conciliaciones_repo import ConciliacionesRepository
from app.infrastructure.db.repositories.finanzas.estado_cuenta_nino_repo import EstadoCuentaNinoRepository
from app.infrastructure.db.repositories.finanzas.libro_caja_repo import LibroCajaRepository
from app.infrastructure.db.repositories.alumnos.alumnos_repo import AlumnosRepository
from app.infrastructure.db.repositories.alumnos.alumnos_paralelos_repo import AlumnosParalelosRepository
from app.infrastructure.db.repositories.finanzas.comprobantes_repo import ComprobantesRepository

from app.infrastructure.db.uow import UnitOfWork
from app.infrastructure.services.jobqueue_service import JobQueueService

# ========================================
# VERIFICADOR DE PERMISOS
# ========================================
def verificar_permisos(usuario: Usuario, permisos_requeridos: list[str]) -> None:
    """Verifica que el usuario tenga al menos uno de los permisos requeridos."""
    if not any(permiso in usuario.permisos for permiso in permisos_requeridos):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Permisos insuficientes. Se requiere uno de: {', '.join(permisos_requeridos)}"
        )


# ========================================
# ROUTER PRINCIPAL
# ========================================
router = APIRouter(prefix="/api/v1/finanzas", tags=["Finanzas"])


# ========================================
# ENDPOINTS - PAGOS
# ========================================
@router.post("/pagos/registrar", tags=["Finanzas - Pagos"], status_code=status.HTTP_201_CREATED)
async def registrar_pago_handler(
    data: dict[str, Any],
    db: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    """Registra un nuevo pago de alumno."""
    permisos_requeridos = ["registrar_pago"]
    verificar_permisos(permisos_requeridos)
    
    try:
        pagos_repo = PagosRepository(db)
        planes_repo = PlanesPagoRepository(db)
        cuotas_repo = CuotasPlanPagoRepository(db)
        estado_cuenta_repo = EstadoCuentaNinoRepository(db)
        comprobantes_repo = ComprobantesRepository(db)
        libro_caja_repo = LibroCajaRepository(db)
        categoria_pago_repo = CategoriasPagoRepository(db)
        uow = UnitOfWork(db)
        jobs = JobQueueService()
        
        use_case = RegistrarPagoUC(
            pagos_repo=pagos_repo,
            planes_repo=planes_repo,
            cuotas_repo=cuotas_repo,
            estado_cuenta_repo=estado_cuenta_repo,
            comprobantes_repo=comprobantes_repo,
            libro_caja_repo=libro_caja_repo,
            categoria_pago_repo=categoria_pago_repo,
            uow=uow,
            jobs=jobs,
        )
        
        resultado = await use_case.execute(
            alumno_id=data["alumno_id"],
            monto=data["monto"],
            metodo_pago=data["metodo_pago"],
            categoria_id=data["categoria_id"],
            fecha_pago=data.get("fecha_pago"),
            observaciones=data.get("observaciones"),
            numero_recibo=data.get("numero_recibo")
        )
        
        return {"success": True, "data": resultado}
    
    except PagoNoEncontradoError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/pagos/listar", tags=["Finanzas - Pagos"])
async def listar_pagos_handler(
    db: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    """Lista todos los pagos de una sede."""
    permisos_requeridos = ["listar_pagos", "ver_finanzas"]
    verificar_permisos(permisos_requeridos)
    
    try:
        pagos_repo = PagosRepository(db)
        use_case = ListarPagosUC(pagos_repo=pagos_repo)
        
        pagos = await use_case.execute()
        return {"success": True, "data": pagos}
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/pagos/{pago_id}/anular", tags=["Finanzas - Pagos"])
async def anular_pago_handler(
    pago_id: int,
    data: dict[str, Any],
    db: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    """Anula un pago existente."""
    permisos_requeridos = ["anular_pago"]
    verificar_permisos(permisos_requeridos)
    
    try:
        pagos_repo = PagosRepository(db)
        cuotas_repo = CuotasPlanPagoRepository(db)
        estado_cuenta_repo = EstadoCuentaNinoRepository(db)
        libro_caja_repo = LibroCajaRepository(db)
        
        use_case = AnularPagoUC(
            pagos_repo=pagos_repo,
            cuotas_repo=cuotas_repo,
            estado_cuenta_repo=estado_cuenta_repo,
            libro_caja_repo=libro_caja_repo
        )
        
        resultado = await use_case.execute(
            pago_id=pago_id,
            motivo_anulacion=data["motivo_anulacion"],
        )
        
        return {"success": True, "data": resultado}
    
    except PagoNoEncontradoError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# ========================================
# ENDPOINTS - PLANES DE PAGO
# ========================================
@router.post("/planes-pago/crear", tags=["Finanzas - Planes de Pago"], status_code=status.HTTP_201_CREATED)
async def crear_plan_pago_handler(
    data: dict[str, Any],
    db: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    """Crea un nuevo plan de pago para un alumno."""
    permisos_requeridos = ["crear_plan_pago"]
    verificar_permisos(permisos_requeridos)
    
    try:
        planes_repo = PlanesPagoRepository(db)
        cuotas_repo = CuotasPlanPagoRepository(db)
        alumnos_repo = AlumnosRepository(db)
        estado_cuenta_repo = EstadoCuentaNinoRepository(db)
        uow = UnitOfWork(db)
        jobs = JobQueueService()
        
        use_case = CrearPlanPagoCU(
            planes_repo=planes_repo,
            cuotas_repo=cuotas_repo,
            alumnos_repo=alumnos_repo,
            estado_cuenta_repo=estado_cuenta_repo,
            uow=uow,
            jobs=jobs,
        )
        
        resultado = await use_case.execute(
            alumno_id=data["alumno_id"],
            monto_total=data["monto_total"],
            numero_cuotas=data["numero_cuotas"],
            fecha_inicio=data["fecha_inicio"],
            
            dia_vencimiento=data.get("dia_vencimiento", 10),
            observaciones=data.get("observaciones")
        )
        
        return {"success": True, "data": resultado}
    
    except PlanPagoNoEncontradoError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/planes-pago/alumno/{alumno_id}", tags=["Finanzas - Planes de Pago"])
async def obtener_plan_pago_alumno_handler(
    alumno_id: int,
    db: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    """Obtiene el plan de pago activo de un alumno."""
    permisos_requeridos = ["ver_plan_pago", "ver_finanzas"]
    verificar_permisos(permisos_requeridos)
    
    try:
        planes_repo = PlanesPagoRepository(db)
        cuotas_repo = CuotasPlanPagoRepository(db)
        
        use_case = ObtenerPlanPagoAlumnoCU(
            planes_repo=planes_repo,
            cuotas_repo=cuotas_repo
        )
        
        plan = await use_case.execute(alumno_id=alumno_id)
        return {"success": True, "data": plan}
    
    except PlanPagoNoEncontradoError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put("/planes-pago/{plan_id}/actualizar-cuotas", tags=["Finanzas - Planes de Pago"])
async def actualizar_cuotas_plan_handler(
    plan_id: int,
    data: dict[str, Any],
    db: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    """Actualiza las cuotas de un plan de pago."""
    permisos_requeridos = ["actualizar_plan_pago"]
    verificar_permisos(permisos_requeridos)
    
    try:
        planes_repo = PlanesPagoRepository(db)
        cuotas_repo = CuotasPlanPagoRepository(db)
        estado_cuenta_repo = EstadoCuentaNinoRepository(db)
        
        use_case = ActualizarCuotasPlanCU(
            planes_repo=planes_repo,
            cuotas_repo=cuotas_repo,
            estado_cuenta_repo=estado_cuenta_repo
        )
        
        resultado = await use_case.execute(
            plan_id=plan_id,
            nuevo_monto_total=data["nuevo_monto_total"],
            nuevo_numero_cuotas=data["nuevo_numero_cuotas"],
        )
        
        return {"success": True, "data": resultado}
    
    except PlanPagoNoEncontradoError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/planes-pago/{plan_id}/tabla-amortizacion", tags=["Finanzas - Planes de Pago"])
async def obtener_tabla_amortizacion_handler(
    plan_id: int,
    db: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    """Obtiene la tabla de amortización de un plan de pago."""
    permisos_requeridos = ["ver_plan_pago", "ver_finanzas"]
    verificar_permisos(permisos_requeridos)
    
    try:
        planes_repo = PlanesPagoRepository(db)
        cuotas_repo = CuotasPlanPagoRepository(db)
        
        use_case = ObtenerTablaAmortizacionCU(
            planes_repo=planes_repo,
            cuotas_repo=cuotas_repo
        )
        
        tabla = await use_case.execute(plan_id=plan_id)
        return {"success": True, "data": tabla}
    
    except PlanPagoNoEncontradoError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# ========================================
# ENDPOINTS - PRORRATEO
# ========================================
@router.post("/prorrateo/calcular", tags=["Finanzas - Prorrateo"])
async def calcular_prorrateo_handler(
    data: dict[str, Any],
    db: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    """Calcula el prorrateo de mensualidad por ingreso tardío."""
    permisos_requeridos = ["calcular_prorrateo"]
    verificar_permisos(permisos_requeridos)
    
    try:
        prorrateos_repo = ProrrateosRepository(db)
        alumnos_paralelos_repo = AlumnosParalelosRepository(db)
        
        use_case = CalcularProrrateoCU(
            prorrateos_repo=prorrateos_repo,
            alumnos_paralelos_repo=alumnos_paralelos_repo
        )
        
        resultado = await use_case.execute(
            alumno_id=data["alumno_id"],
            fecha_ingreso=data["fecha_ingreso"],
            monto_mensual_completo=data["monto_mensual_completo"],
        )
        
        return {"success": True, "data": resultado}
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# ========================================
# ENDPOINTS - EGRESOS
# ========================================
@router.post("/egresos/registrar", tags=["Finanzas - Egresos"], status_code=status.HTTP_201_CREATED)
async def registrar_egreso_handler(
    data: dict[str, Any],
    db: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    """Registra un nuevo egreso."""
    permisos_requeridos = ["registrar_egreso"]
    verificar_permisos(permisos_requeridos)
    
    try:
        egresos_repo = EgresosRepository(db)
        categorias_repo = CategoriaEgresoRepository(db)
        libro_caja_repo = LibroCajaRepository(db)
        
        use_case = RegistrarEgresoUC(
            egresos_repo=egresos_repo,
            categorias_repo=categorias_repo,
            libro_caja_repo=libro_caja_repo
        )
        
        resultado = await use_case.execute(
            monto=data["monto"],
            categoria_id=data["categoria_id"],
            descripcion=data["descripcion"],
            fecha_egreso=data.get("fecha_egreso"),
            comprobante_numero=data.get("comprobante_numero")
        )
        
        return {"success": True, "data": resultado}
    
    except CategoriaEgresoNoEncontradaError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/egresos/listar", tags=["Finanzas - Egresos"])
async def listar_egresos_handler(
    db: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    """Lista todos los egresos de una sede."""
    permisos_requeridos = ["listar_egresos", "ver_finanzas"]
    verificar_permisos(permisos_requeridos)
    
    try:
        egresos_repo = EgresosRepository(db)
        use_case = ListarEgresosUC(egresos_repo=egresos_repo)
        
        egresos = await use_case.execute()
        return {"success": True, "data": egresos}
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/egresos/{egreso_id}/anular", tags=["Finanzas - Egresos"])
async def anular_egreso_handler(
    egreso_id: int,
    data: dict[str, Any],
    db: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    """Anula un egreso existente."""
    permisos_requeridos = ["anular_egreso"]
    verificar_permisos(permisos_requeridos)
    
    try:
        egresos_repo = EgresosRepository(db)
        libro_caja_repo = LibroCajaRepository(db)
        
        use_case = AnularEgresoUC(
            egresos_repo=egresos_repo,
            libro_caja_repo=libro_caja_repo
        )
        
        resultado = await use_case.execute(
            egreso_id=egreso_id,
            motivo_anulacion=data["motivo_anulacion"],
        )
        
        return {"success": True, "data": resultado}
    
    except EgresoNoEncontradoError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# ========================================
# ENDPOINTS - DESCUENTOS
# ========================================
@router.post("/descuentos/aplicar", tags=["Finanzas - Descuentos"])
async def aplicar_descuento_handler(
    data: dict[str, Any],
    db: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    """Aplica un descuento a un alumno."""
    permisos_requeridos = ["aplicar_descuento"]
    verificar_permisos(permisos_requeridos)
    
    try:
        descuentos_repo = DescuentosRepository(db)
        alumnos_repo = AlumnosRepository(db)
        estado_cuenta_repo = EstadoCuentaNinoRepository(db)
        uow = UnitOfWork(db)
        jobs = JobQueueService()
        
        use_case = AplicarDescuentoCU(
            descuentos_repo=descuentos_repo,
            alumnos_repo=alumnos_repo,
            estado_cuenta_repo=estado_cuenta_repo,
            uow=uow,
            jobs=jobs,
        )
        
        resultado = await use_case.execute(
            alumno_id=data["alumno_id"],
            tipo_descuento=data["tipo_descuento"],
            porcentaje=data["porcentaje"],
            observaciones=data.get("observaciones")
        )
        
        return {"success": True, "data": resultado}
    
    except DescuentoNoEncontradoError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/descuentos/calcular-disponible/{alumno_id}", tags=["Finanzas - Descuentos"])
async def calcular_descuento_disponible_handler(
    alumno_id: int,
    db: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    """Calcula el descuento disponible para un alumno."""
    permisos_requeridos = ["ver_descuentos", "ver_finanzas"]
    verificar_permisos(permisos_requeridos)
    
    try:
        descuentos_repo = DescuentosRepository(db)
        alumnos_repo = AlumnosRepository(db)
        
        use_case = CalcularDescuentoDisponibleCU(
            descuentos_repo=descuentos_repo,
            alumnos_repo=alumnos_repo
        )
        
        descuento = await use_case.execute(alumno_id=alumno_id)
        return {"success": True, "data": descuento}
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# ========================================
# ENDPOINTS - ARQUEO
# ========================================
@router.post("/arqueo/generar-mensual", tags=["Finanzas - Arqueo"], status_code=status.HTTP_201_CREATED)
async def generar_arqueo_mensual_handler(
    data: dict[str, Any],
    db: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    """Genera el arqueo de caja mensual."""
    permisos_requeridos = ["generar_arqueo"]
    verificar_permisos(permisos_requeridos)
    
    try:
        arqueos_repo = ArqueosRepository(db)
        pagos_repo = PagosRepository(db)
        egresos_repo = EgresosRepository(db)
        
        use_case = GenerarArqueoMensualUseCase(
            arqueos_repo=arqueos_repo,
            pagos_repo=pagos_repo,
            egresos_repo=egresos_repo
        )
        
        resultado = await use_case.execute(
            mes=data["mes"],
            anio=data["anio"],
        )
        
        return {"success": True, "data": resultado}
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/arqueo/listar", tags=["Finanzas - Arqueo"])
async def listar_arqueos_handler(
    db: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    """Lista todos los arqueos de una sede."""
    permisos_requeridos = ["ver_arqueos", "ver_finanzas"]
    verificar_permisos(permisos_requeridos)
    
    try:
        arqueos_repo = ArqueosRepository(db)
        use_case = ListarArqueosUseCase(arqueos_repo=arqueos_repo)
        
        arqueos = await use_case.execute()
        return {"success": True, "data": arqueos}
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put("/arqueo/{arqueo_id}/recalcular", tags=["Finanzas - Arqueo"])
async def recalcular_arqueo_handler(
    arqueo_id: int,
    db: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    """Recalcula un arqueo existente."""
    permisos_requeridos = ["recalcular_arqueo"]
    verificar_permisos(permisos_requeridos)
    
    try:
        arqueos_repo = ArqueosRepository(db)
        pagos_repo = PagosRepository(db)
        egresos_repo = EgresosRepository(db)
        
        use_case = RecalcularArqueoUseCase(
            arqueos_repo=arqueos_repo,
            pagos_repo=pagos_repo,
            egresos_repo=egresos_repo
        )
        
        resultado = await use_case.execute(
            arqueo_id=arqueo_id,
        )
        
        return {"success": True, "data": resultado}
    
    except ArqueoNoEncontradoError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# ========================================
# ENDPOINTS - CATEGORÍA EGRESO
# ========================================
@router.post("/categorias-egreso/crear", tags=["Finanzas - Categorías Egreso"], status_code=status.HTTP_201_CREATED)
async def crear_categoria_egreso_handler(
    data: dict[str, Any],
    db: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    """Crea una nueva categoría de egreso."""
    permisos_requeridos = ["crear_categoria_egreso"]
    verificar_permisos(permisos_requeridos)
    
    try:
        categorias_repo = CategoriaEgresoRepository(db)
        use_case = CrearCategoriaEgresoUseCase(categorias_repo=categorias_repo)
        
        resultado = await use_case.execute(
            nombre=data["nombre"],
            descripcion=data.get("descripcion"),
        )
        
        return {"success": True, "data": resultado}
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/categorias-egreso/listar", tags=["Finanzas - Categorías Egreso"])
async def listar_categorias_egreso_handler(
    db: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    """Lista todas las categorías de egreso."""
    permisos_requeridos = ["ver_categorias_egreso", "ver_finanzas"]
    verificar_permisos(permisos_requeridos)
    
    try:
        categorias_repo = CategoriaEgresoRepository(db)
        use_case = ListarCategoriasEgresoUseCase(categorias_repo=categorias_repo)
        
        categorias = await use_case.execute()
        return {"success": True, "data": categorias}
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put("/categorias-egreso/{categoria_id}/actualizar", tags=["Finanzas - Categorías Egreso"])
async def actualizar_categoria_egreso_handler(
    categoria_id: int,
    data: dict[str, Any],
    db: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    """Actualiza una categoría de egreso."""
    permisos_requeridos = ["actualizar_categoria_egreso"]
    verificar_permisos(permisos_requeridos)
    
    try:
        categorias_repo = CategoriaEgresoRepository(db)
        use_case = ActualizarCategoriaEgresoUseCase(categorias_repo=categorias_repo)
        
        resultado = await use_case.execute(
            categoria_id=categoria_id,
            nombre=data.get("nombre"),
            descripcion=data.get("descripcion"),
            activo=data.get("activo"),
        )
        
        return {"success": True, "data": resultado}
    
    except CategoriaEgresoNoEncontradaError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# ========================================
# ENDPOINTS - CATEGORÍA PAGO
# ========================================
@router.post("/categorias-pago/crear", tags=["Finanzas - Categorías Pago"], status_code=status.HTTP_201_CREATED)
async def crear_categoria_pago_handler(
    data: dict[str, Any],
    db: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    """Crea una nueva categoría de pago."""
    permisos_requeridos = ["crear_categoria_pago"]
    verificar_permisos(permisos_requeridos)
    
    try:
        categorias_repo = CategoriasPagoRepository(db)
        use_case = CrearCategoriaPagoUseCase(categorias_repo=categorias_repo)
        
        resultado = await use_case.execute(
            nombre=data["nombre"],
            descripcion=data.get("descripcion"),
            codigo=data.get("codigo"),
        )
        
        return {"success": True, "data": resultado}
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/categorias-pago/listar", tags=["Finanzas - Categorías Pago"])
async def listar_categorias_pago_handler(
    db: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    """Lista todas las categorías de pago."""
    permisos_requeridos = ["ver_categorias_pago", "ver_finanzas"]
    verificar_permisos(permisos_requeridos)
    
    try:
        categorias_repo = CategoriasPagoRepository(db)
        use_case = ListarCategoriasPagoUseCase(categorias_repo=categorias_repo)
        
        categorias = await use_case.execute()
        return {"success": True, "data": categorias}
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put("/categorias-pago/{categoria_id}/actualizar", tags=["Finanzas - Categorías Pago"])
async def actualizar_categoria_pago_handler(
    categoria_id: int,
    data: dict[str, Any],
    db: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    """Actualiza una categoría de pago."""
    permisos_requeridos = ["actualizar_categoria_pago"]
    verificar_permisos(permisos_requeridos)
    
    try:
        categorias_repo = CategoriasPagoRepository(db)
        use_case = ActualizarCategoriaPagoUseCase(categorias_repo=categorias_repo)
        
        resultado = await use_case.execute(
            categoria_id=categoria_id,
            nombre=data.get("nombre"),
            descripcion=data.get("descripcion"),
            codigo=data.get("codigo"),
            activo=data.get("activo"),
        )
        
        return {"success": True, "data": resultado}
    
    except CategoriaPagoNoEncontradaError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# ========================================
# ENDPOINTS - CONCILIACIONES
# ========================================
@router.put("/conciliaciones/pago/{pago_id}/marcar-depositado", tags=["Finanzas - Conciliaciones"])
async def marcar_pago_depositado_handler(
    pago_id: int,
    data: dict[str, Any],
    db: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    """Marca un pago como depositado en banco."""
    permisos_requeridos = ["conciliar_pagos"]
    verificar_permisos(permisos_requeridos)
    
    try:
        conciliaciones_repo = ConciliacionesRepository(db)
        pagos_repo = PagosRepository(db)
        
        use_case = MarcarPagoDepositadoCU(
            conciliaciones_repo=conciliaciones_repo,
            pagos_repo=pagos_repo
        )
        
        resultado = await use_case.execute(
            pago_id=pago_id,
            fecha_deposito=data["fecha_deposito"],
            numero_boleta=data["numero_boleta"],
        )
        
        return {"success": True, "data": resultado}
    
    except ConciliacionError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put("/conciliaciones/pago/{pago_id}/marcar-transferido", tags=["Finanzas - Conciliaciones"])
async def marcar_pago_transferido_handler(
    pago_id: int,
    data: dict[str, Any],
    db: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    """Marca un pago como transferido a otra sede."""
    permisos_requeridos = ["conciliar_pagos"]
    verificar_permisos(permisos_requeridos)
    
    try:
        conciliaciones_repo = ConciliacionesRepository(db)
        pagos_repo = PagosRepository(db)
        
        use_case = MarcarPagoTransferidoCU(
            conciliaciones_repo=conciliaciones_repo,
            pagos_repo=pagos_repo
        )
        
        resultado = await use_case.execute(
            pago_id=pago_id,
            sede_destino_id=data["sede_destino_id"],
            fecha_transferencia=data["fecha_transferencia"],
            numero_transaccion=data["numero_transaccion"],
        )
        
        return {"success": True, "data": resultado}
    
    except ConciliacionError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/conciliaciones/pendientes-transferir", tags=["Finanzas - Conciliaciones"])
async def listar_pendientes_transferir_handler(
    db: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    """Lista pagos pendientes de transferencia."""
    permisos_requeridos = ["ver_conciliaciones", "ver_finanzas"]
    verificar_permisos(permisos_requeridos)
    
    try:
        conciliaciones_repo = ConciliacionesRepository(db)
        pagos_repo = PagosRepository(db)
        
        use_case = ListarPendientesTransferirCU(
            conciliaciones_repo=conciliaciones_repo,
            pagos_repo=pagos_repo
        )
        
        pendientes = await use_case.execute()
        return {"success": True, "data": pendientes}
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/conciliaciones/verificar", tags=["Finanzas - Conciliaciones"])
async def verificar_conciliacion_handler(
    data: dict[str, Any],
    db: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    """Verifica la conciliación bancaria de un período."""
    permisos_requeridos = ["verificar_conciliacion"]
    verificar_permisos(permisos_requeridos)
    
    try:
        conciliaciones_repo = ConciliacionesRepository(db)
        pagos_repo = PagosRepository(db)
        
        use_case = VerificarConciliacionCU(
            conciliaciones_repo=conciliaciones_repo,
            pagos_repo=pagos_repo
        )
        
        resultado = await use_case.execute(
            fecha_inicio=data["fecha_inicio"],
            fecha_fin=data["fecha_fin"],
        )
        
        return {"success": True, "data": resultado}
    
    except ConciliacionError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/conciliaciones/historial-transferencias", tags=["Finanzas - Conciliaciones"])
async def obtener_historial_transferencias_handler(
    db: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    """Obtiene el historial de transferencias entre sedes."""
    permisos_requeridos = ["ver_conciliaciones", "ver_finanzas"]
    verificar_permisos(permisos_requeridos)
    
    try:
        conciliaciones_repo = ConciliacionesRepository(db)
        pagos_repo = PagosRepository(db)
        
        use_case = ObtenerHistorialTransferenciasCU(
            conciliaciones_repo=conciliaciones_repo,
            pagos_repo=pagos_repo
        )
        
        historial = await use_case.execute()
        return {"success": True, "data": historial}
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# ========================================
# ENDPOINTS - DASHBOARD
# ========================================
@router.get("/dashboard/sede", tags=["Finanzas - Dashboard"])
async def obtener_dashboard_sede_handler(
    db: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    """Obtiene el dashboard general de la sede."""
    permisos_requeridos = ["ver_dashboard", "ver_finanzas"]
    verificar_permisos(permisos_requeridos)
    
    try:
        pagos_repo = PagosRepository(db)
        egresos_repo = EgresosRepository(db)
        alumnos_repo = AlumnosRepository(db)
        estado_cuenta_repo = EstadoCuentaNinoRepository(db)
        
        use_case = ObtenerDashboardSedeCU(
            pagos_repo=pagos_repo,
            egresos_repo=egresos_repo,
            alumnos_repo=alumnos_repo,
            estado_cuenta_repo=estado_cuenta_repo
        )
        
        dashboard = await use_case.execute()
        return {"success": True, "data": dashboard}
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/dashboard/asistencia-promedio", tags=["Finanzas - Dashboard"])
async def obtener_asistencia_promedio_handler(
    db: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    """Obtiene el promedio de asistencia."""
    permisos_requeridos = ["ver_dashboard", "ver_finanzas"]
    verificar_permisos(permisos_requeridos)
    
    try:
        from app.infrastructure.db.repositories.alumnos.asistencia_alumnos_repo import AsistenciaAlumnosRepository
        
        asistencia_repo = AsistenciaAlumnosRepository(db)
        alumnos_repo = AlumnosRepository(db)
        
        use_case = ObtenerAsistenciaPromedioCU(
            asistencia_repo=asistencia_repo,
            alumnos_repo=alumnos_repo
        )
        
        resultado = await use_case.execute()
        return {"success": True, "data": resultado}
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/dashboard/nuevos-inscritos-por-mes", tags=["Finanzas - Dashboard"])
async def obtener_nuevos_inscritos_por_mes_handler(
    db: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    """Obtiene el número de nuevos inscritos por mes."""
    permisos_requeridos = ["ver_dashboard", "ver_finanzas"]
    verificar_permisos(permisos_requeridos)
    
    try:
        alumnos_repo = AlumnosRepository(db)
        
        use_case = ObtenerNuevosInscritosPorMesCU(alumnos_repo=alumnos_repo)
        resultado = await use_case.execute()
        
        return {"success": True, "data": resultado}
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/dashboard/inscritos-por-mes", tags=["Finanzas - Dashboard"])
async def obtener_inscritos_por_mes_handler(
    db: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    """Obtiene el total de inscritos por mes."""
    permisos_requeridos = ["ver_dashboard", "ver_finanzas"]
    verificar_permisos(permisos_requeridos)
    
    try:
        alumnos_repo = AlumnosRepository(db)
        
        use_case = ObtenerInscritosPorMesCU(alumnos_repo=alumnos_repo)
        resultado = await use_case.execute()
        
        return {"success": True, "data": resultado}
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/dashboard/ingresos-egresos-mes", tags=["Finanzas - Dashboard"])
async def obtener_ingresos_egresos_mes_handler(
    db: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    """Obtiene ingresos y egresos mensuales."""
    permisos_requeridos = ["ver_dashboard", "ver_finanzas"]
    verificar_permisos(permisos_requeridos)
    
    try:
        pagos_repo = PagosRepository(db)
        egresos_repo = EgresosRepository(db)
        
        use_case = ObtenerIngresosEgresosMesCU(
            pagos_repo=pagos_repo,
            egresos_repo=egresos_repo
        )
        
        resultado = await use_case.execute()
        return {"success": True, "data": resultado}
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/dashboard/ocupacion-paralelos", tags=["Finanzas - Dashboard"])
async def obtener_ocupacion_paralelos_handler(
    db: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    """Obtiene la ocupación de paralelos."""
    permisos_requeridos = ["ver_dashboard", "ver_finanzas"]
    verificar_permisos(permisos_requeridos)
    
    try:
        from app.infrastructure.db.repositories.academico.paralelos_repo import ParalelosRepository
        
        paralelos_repo = ParalelosRepository(db)
        alumnos_paralelos_repo = AlumnosParalelosRepository(db)
        
        use_case = ObtenerOcupacionParalelosCU(
            paralelos_repo=paralelos_repo,
            alumnos_paralelos_repo=alumnos_paralelos_repo
        )
        
        resultado = await use_case.execute()
        return {"success": True, "data": resultado}
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/dashboard/pagos-por-categoria", tags=["Finanzas - Dashboard"])
async def obtener_pagos_por_categoria_handler(
    db: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    """Obtiene pagos agrupados por categoría."""
    permisos_requeridos = ["ver_dashboard", "ver_finanzas"]
    verificar_permisos(permisos_requeridos)
    
    try:
        pagos_repo = PagosRepository(db)
        categorias_repo = CategoriasPagoRepository(db)
        
        use_case = ObtenerPagosPorCategoriaCU(
            pagos_repo=pagos_repo,
            categorias_repo=categorias_repo
        )
        
        resultado = await use_case.execute()
        return {"success": True, "data": resultado}
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/dashboard/rentabilidad-sede", tags=["Finanzas - Dashboard"])
async def obtener_rentabilidad_sede_handler(
    db: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    """Obtiene la rentabilidad de la sede."""
    permisos_requeridos = ["ver_dashboard", "ver_finanzas"]
    verificar_permisos(permisos_requeridos)
    
    try:
        pagos_repo = PagosRepository(db)
        egresos_repo = EgresosRepository(db)
        
        use_case = ObtenerRentabilidadSedeCU(
            pagos_repo=pagos_repo,
            egresos_repo=egresos_repo
        )
        
        resultado = await use_case.execute()
        return {"success": True, "data": resultado}
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/dashboard/reporte-deudores", tags=["Finanzas - Dashboard"])
async def obtener_reporte_deudores_handler(
    db: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    """Obtiene el reporte de alumnos deudores."""
    permisos_requeridos = ["ver_dashboard", "ver_finanzas"]
    verificar_permisos(permisos_requeridos)
    
    try:
        estado_cuenta_repo = EstadoCuentaNinoRepository(db)
        alumnos_repo = AlumnosRepository(db)
        
        use_case = ObtenerReporteDeudoresCU(
            estado_cuenta_repo=estado_cuenta_repo,
            alumnos_repo=alumnos_repo
        )
        
        resultado = await use_case.execute()
        return {"success": True, "data": resultado}
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# ========================================
# ENDPOINTS - ESTADO DE CUENTA
# ========================================
@router.get("/estado-cuenta/alumno/{alumno_id}/detallado", tags=["Finanzas - Estado de Cuenta"])
async def obtener_estado_cuenta_detallado_handler(
    alumno_id: int,
    db: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    """Obtiene el estado de cuenta detallado de un alumno."""
    permisos_requeridos = ["ver_estado_cuenta", "ver_finanzas"]
    verificar_permisos(permisos_requeridos)
    
    try:
        estado_cuenta_repo = EstadoCuentaNinoRepository(db)
        pagos_repo = PagosRepository(db)
        planes_repo = PlanesPagoRepository(db)
        descuentos_repo = DescuentosRepository(db)
        
        use_case = ObtenerEstadoCuentaDetalladoCU(
            estado_cuenta_repo=estado_cuenta_repo,
            pagos_repo=pagos_repo,
            planes_repo=planes_repo,
            descuentos_repo=descuentos_repo
        )
        
        estado = await use_case.execute(alumno_id=alumno_id)
        return {"success": True, "data": estado}
    
    except EstadoCuentaError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/estado-cuenta/alumnos-morosos", tags=["Finanzas - Estado de Cuenta"])
async def listar_alumnos_morosos_handler(
    db: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    """Lista todos los alumnos con mora."""
    permisos_requeridos = ["ver_estado_cuenta", "ver_finanzas"]
    verificar_permisos(permisos_requeridos)
    
    try:
        estado_cuenta_repo = EstadoCuentaNinoRepository(db)
        alumnos_repo = AlumnosRepository(db)
        cuotas_repo = CuotasPlanPagoRepository(db)
        
        use_case = ListarAlumnosMorososCU(
            estado_cuenta_repo=estado_cuenta_repo,
            alumnos_repo=alumnos_repo,
            cuotas_repo=cuotas_repo
        )
        
        morosos = await use_case.execute()
        return {"success": True, "data": morosos}
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/estado-cuenta/alumno/{alumno_id}/enviar-recordatorio", tags=["Finanzas - Estado de Cuenta"])
async def enviar_recordatorio_pago_handler(
    alumno_id: int,
    db: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    """Envía recordatorio de pago a tutores de un alumno."""
    permisos_requeridos = ["enviar_recordatorio_pago"]
    verificar_permisos(permisos_requeridos)
    
    try:
        estado_cuenta_repo = EstadoCuentaNinoRepository(db)
        alumnos_repo = AlumnosRepository(db)
        from app.infrastructure.db.repositories.alumnos.tutores_repo import TutoresRepository
        from app.infrastructure.db.repositories.comunicaciones.notificaciones_repo import NotificacionesRepository
        
        tutores_repo = TutoresRepository(db)
        notificaciones_repo = NotificacionesRepository(db)
        uow = UnitOfWork(db)
        jobs = JobQueueService()
        
        use_case = EnviarRecordatorioPagoCU(
            estado_cuenta_repo=estado_cuenta_repo,
            alumnos_repo=alumnos_repo,
            tutores_repo=tutores_repo,
            notificaciones_repo=notificaciones_repo,
            uow=uow,
            jobs=jobs,
        )
        
        resultado = await use_case.execute(
            alumno_id=alumno_id,
        )
        
        return {"success": True, "data": resultado}
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/estado-cuenta/alumno/{alumno_id}/verificar-mora", tags=["Finanzas - Estado de Cuenta"])
async def verificar_alumno_moroso_handler(
    alumno_id: int,
    db: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    """Verifica si un alumno está en mora."""
    permisos_requeridos = ["ver_estado_cuenta", "ver_finanzas"]
    verificar_permisos(permisos_requeridos)
    
    try:
        estado_cuenta_repo = EstadoCuentaNinoRepository(db)
        cuotas_repo = CuotasPlanPagoRepository(db)
        
        use_case = VerificarAlumnoMorosoCU(
            estado_cuenta_repo=estado_cuenta_repo,
            cuotas_repo=cuotas_repo
        )
        
        resultado = await use_case.execute(alumno_id=alumno_id)
        return {"success": True, "data": resultado}
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# ========================================
# ENDPOINTS - LIBRO CAJA
# ========================================
@router.post("/libro-caja/registrar-ingreso", tags=["Finanzas - Libro Caja"], status_code=status.HTTP_201_CREATED)
async def registrar_ingreso_caja_handler(
    data: dict[str, Any],
    db: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    """Registra un ingreso en el libro de caja."""
    permisos_requeridos = ["registrar_movimiento_caja"]
    verificar_permisos(permisos_requeridos)
    
    try:
        libro_caja_repo = LibroCajaRepository(db)
        
        use_case = RegistrarIngresoCajaUseCase(libro_caja_repo=libro_caja_repo)
        
        resultado = await use_case.execute(
            monto=data["monto"],
            concepto=data["concepto"],
            categoria=data["categoria"],
            fecha_movimiento=data.get("fecha_movimiento"),
            referencia=data.get("referencia")
        )
        
        return {"success": True, "data": resultado}
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/libro-caja/registrar-egreso", tags=["Finanzas - Libro Caja"], status_code=status.HTTP_201_CREATED)
async def registrar_egreso_caja_handler(
    data: dict[str, Any],
    db: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    """Registra un egreso en el libro de caja."""
    permisos_requeridos = ["registrar_movimiento_caja"]
    verificar_permisos(permisos_requeridos)
    
    try:
        libro_caja_repo = LibroCajaRepository(db)
        
        use_case = RegistrarEgresoCajaUseCase(libro_caja_repo=libro_caja_repo)
        
        resultado = await use_case.execute(
            monto=data["monto"],
            concepto=data["concepto"],
            categoria=data["categoria"],
            fecha_movimiento=data.get("fecha_movimiento"),
            referencia=data.get("referencia")
        )
        
        return {"success": True, "data": resultado}
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/libro-caja/movimientos", tags=["Finanzas - Libro Caja"])
async def listar_movimientos_caja_handler(
    db: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    """Lista todos los movimientos del libro de caja."""
    permisos_requeridos = ["ver_libro_caja", "ver_finanzas"]
    verificar_permisos(permisos_requeridos)
    
    try:
        libro_caja_repo = LibroCajaRepository(db)
        use_case = ListarMovimientosCajaUseCase(libro_caja_repo=libro_caja_repo)
        
        movimientos = await use_case.execute()
        return {"success": True, "data": movimientos}
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/libro-caja/saldo-sede", tags=["Finanzas - Libro Caja"])
async def obtener_saldo_sede_handler(
    db: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    """Obtiene el saldo actual de la sede."""
    permisos_requeridos = ["ver_libro_caja", "ver_finanzas"]
    verificar_permisos(permisos_requeridos)
    
    try:
        libro_caja_repo = LibroCajaRepository(db)
        use_case = ObtenerSaldoSedeUseCase(libro_caja_repo=libro_caja_repo)
        
        saldo = await use_case.execute()
        return {"success": True, "data": saldo}
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/libro-caja/totales-periodo", tags=["Finanzas - Libro Caja"])
async def obtener_totales_periodo_handler(
    db: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    """Obtiene totales de ingresos/egresos de un período."""
    permisos_requeridos = ["ver_libro_caja", "ver_finanzas"]
    verificar_permisos(permisos_requeridos)
    
    try:
        libro_caja_repo = LibroCajaRepository(db)
        use_case = ObtenerTotalesPeriodoUseCase(libro_caja_repo=libro_caja_repo)
        
        totales = await use_case.execute()
        return {"success": True, "data": totales}
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

# app/kernel/domain/finanzas/ports.py
from typing import Protocol, Optional, List, Dict, Any
from decimal import Decimal
from datetime import date, datetime
from app.kernel.domain.finanzas.cuota_plan_pago_entidad import CuotaPlanPagoEntidad
from app.kernel.domain.finanzas.plan_pago_entidad import PlanPagoEntidad
# ==================== REPOSITORIOS ====================

class IPagoRepository(Protocol):
    """Puerto: Repositorio de pagos."""
    
    async def crear(
        self,
        alumno_id: int,
        monto_pagado: Decimal,
        fecha_pago: datetime,
        metodo_pago: str,
        categoria_pago_id: int,
        numero_comprobante: Optional[str],
        observaciones: Optional[str],
        registrado_por: int,
        sede_id: Optional[int]
    ) -> int: ...
    
    async def obtener_por_id(self, pago_id: int) -> Optional[Dict[str, Any]]: ...
    
    async def listar(
        self,
        sede_id: Optional[int] = None,
        alumno_id: Optional[int] = None,
        fecha_desde: Optional[date] = None,
        fecha_hasta: Optional[date] = None,
        metodo_pago: Optional[str] = None,
        incluir_anulados: bool = False,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]: ...
    
    async def contar(
        self,
        sede_id: Optional[int] = None,
        alumno_id: Optional[int] = None,
        fecha_desde: Optional[date] = None,
        fecha_hasta: Optional[date] = None,
        metodo_pago: Optional[str] = None,
        incluir_anulados: bool = False
    ) -> int: ...
    
    async def anular(
        self,
        pago_id: int,
        anulado_por_id: int,
        motivo: str
    ) -> bool: ...
    
    async def verificar_duplicado_comprobante(self, numero: str) -> bool: ...


class IEgresoRepository(Protocol):
    """Puerto: Repositorio de egresos."""
    
    async def crear(
        self,
        sede_id: int,
        monto: Decimal,
        categoria_egreso_id: int,
        descripcion: str,
        fecha_egreso: datetime,
        numero_comprobante: Optional[str],
        observaciones: Optional[str],
        registrado_por: int
    ) -> int: ...
    
    async def obtener_por_id(self, egreso_id: int) -> Optional[Dict[str, Any]]: ...
    
    async def listar(
        self,
        sede_id: Optional[int] = None,
        categoria_id: Optional[int] = None,
        fecha_desde: Optional[date] = None,
        fecha_hasta: Optional[date] = None,
        incluir_anulados: bool = False,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]: ...
    
    async def contar(
        self,
        sede_id: Optional[int] = None,
        categoria_id: Optional[int] = None,
        fecha_desde: Optional[date] = None,
        fecha_hasta: Optional[date] = None,
        incluir_anulados: bool = False
    ) -> int: ...
    
    async def anular(
        self,
        egreso_id: int,
        anulado_por_id: int,
        motivo: str
    ) -> bool: ...
    
    async def verificar_duplicado_comprobante(self, numero: str) -> bool: ...
    
    async def calcular_total_periodo(
        self,
        sede_id: Optional[int],
        fecha_desde: date,
        fecha_hasta: date,
        incluir_anulados: bool = False
    ) -> Decimal: ...


class IEstadoCuentaNinoRepository(Protocol):
    """Puerto: Repositorio de estado de cuenta de niño."""
    
    async def obtener_por_alumno(
        self,
        alumno_id: int
    ) -> Optional[Dict[str, Any]]: ...
    
    async def crear(
        self,
        alumno_id: int,
        total_deuda: Decimal,
        total_pagado: Decimal,
        saldo_pendiente: Decimal
    ) -> int: ...
    
    async def registrar_pago(
        self,
        alumno_id: int,
        monto: Decimal
    ) -> None: ...
    
    async def registrar_cargo(
        self,
        alumno_id: int,
        monto: Decimal
    ) -> None: ...
    
    async def calcular_saldo(
        self,
        alumno_id: int
    ) -> Decimal: ...
    
    async def listar_deudores(
        self,
        sede_id: Optional[int] = None,
        limite: int = 100
    ) -> List[Dict[str, Any]]: ...
    
    async def actualizar_saldo_pendiente(
        self,
        alumno_id: int,
        nuevo_saldo: Decimal
    ) -> bool: ...
    
    async def obtener_historial_movimientos(
        self,
        alumno_id: int,
        fecha_desde: Optional[date] = None,
        fecha_hasta: Optional[date] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]: ...


class ILibroCajaRepository(Protocol):
    """Puerto: Repositorio de libro de caja."""
    
    async def registrar_ingreso(
        self,
        monto: Decimal,
        fecha: datetime,
        registrado_por_id: int,
        observaciones: str,
        pago_id: Optional[int] = None,
        sede_id: Optional[int] = None
    ) -> int: ...
    
    async def registrar_egreso(
        self,
        monto: Decimal,
        fecha: datetime,
        registrado_por_id: int,
        observaciones: str,
        egreso_id: Optional[int] = None,
        sede_id: Optional[int] = None
    ) -> int: ...
    
    async def obtener_saldo_actual(
        self,
        sede_id: Optional[int] = None,
        hasta_fecha: Optional[datetime] = None
    ) -> Decimal: ...
    
    async def listar_movimientos(
        self,
        fecha_desde: date,
        fecha_hasta: date,
        sede_id: Optional[int] = None,
        tipo_movimiento: Optional[str] = None,
        limit: int = 500,
        offset: int = 0
    ) -> List[Dict[str, Any]]: ...
    
    async def calcular_totales_periodo(
        self,
        fecha_desde: date,
        fecha_hasta: date,
        sede_id: Optional[int] = None
    ) -> Dict[str, Any]: ...


class IPlanCuotaRepository(Protocol):
    """Puerto: Repositorio de cuotas de planes de pago."""
    
    async def listar_por_plan(
        self,
        plan_pago_id: int,
        estado: Optional[str] = None
    ) -> List[Dict[str, Any]]: ...
    
    async def obtener_proxima_pendiente(
        self,
        plan_pago_id: int
    ) -> Optional[Dict[str, Any]]: ...
    
    async def marcar_vencidas(self) -> int: ...
    
    async def registrar_pago_cuota(
        self,
        cuota_id: int,
        monto_pagado: Decimal,
        pago_id: Optional[int] = None
    ) -> bool: ...

    async def obtener_por_alumno(
        self,
        alumno_id: int,
        sede_id: int,
        solo_activo: bool = True
    ) -> Optional[PlanPagoEntidad]:
        """
        Obtiene el plan de pago de un alumno.
        
        Args:
            alumno_id: ID del alumno
            sede_id: ID de la sede (segregación)
            solo_activo: Si True, solo retorna planes con estado='activo'
        
        Returns:
            Plan de pago del alumno o None si no existe
        """
        ...


class IArqueoRepository(Protocol):
    """Puerto: Repositorio de arqueos de caja."""
    
    async def crear(self, arqueo_data: dict) -> int: ...
    async def cerrar(self, arqueo_id: int, cerrado_por_id: int) -> bool: ...
    async def listar(
        self,
        sede_id: Optional[int] = None,
        fecha_desde: Optional[date] = None,
        fecha_hasta: Optional[date] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]: ...


class IComprobanteRepository(Protocol):
    """Puerto: Repositorio de comprobantes."""
    
    async def crear(self, comprobante_data: dict) -> int: ...
    async def obtener(self, comprobante_id: int) -> Optional[Dict[str, Any]]: ...
    async def listar(
        self,
        sede_id: Optional[int] = None,
        tipo: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]: ...


class IConciliacionRepository(Protocol):
    """Puerto: Repositorio de conciliaciones bancarias."""
    
    async def crear(self, conciliacion_data: dict) -> int: ...
    async def marcar_conciliado(self, conciliacion_id: int) -> bool: ...
    async def reversar(self, conciliacion_id: int, revertido_por_id: int) -> bool: ...


class ICategoriaPagoRepository(Protocol):
    """Puerto: Repositorio de categorías de pago."""
    
    async def crear(
        self,
        nombre: str,
        descripcion: Optional[str],
        sede_id: int
    ) -> int: ...
    
    async def obtener_por_id(self, categoria_id: int) -> Optional[Dict[str, Any]]: ...
    
    async def listar(
        self,
        sede_id: Optional[int] = None,
        activo: Optional[bool] = True
    ) -> List[Dict[str, Any]]: ...
    
    async def actualizar(
        self,
        categoria_id: int,
        nombre: Optional[str] = None,
        descripcion: Optional[str] = None,
        activo: Optional[bool] = None
    ) -> bool: ...


class ICategoriaEgresoRepository(Protocol):
    """Puerto: Repositorio de categorías de egreso."""
    
    async def crear(
        self,
        nombre: str,
        descripcion: Optional[str],
        sede_id: int
    ) -> int: ...
    
    async def obtener_por_id(self, categoria_id: int) -> Optional[Dict[str, Any]]: ...
    
    async def listar(
        self,
        sede_id: Optional[int] = None,
        activo: Optional[bool] = True
    ) -> List[Dict[str, Any]]: ...
    
    async def actualizar(
        self,
        categoria_id: int,
        nombre: Optional[str] = None,
        descripcion: Optional[str] = None,
        activo: Optional[bool] = None
    ) -> bool: ...


# ==================== SERVICIOS DE DOMINIO ====================

class ICalculadorDescuento(Protocol):
    """Puerto: Servicio de cálculo de descuentos."""
    
    async def calcular_disponible(
        self,
        alumno_id: int,
        tipo_descuento: str
    ) -> Decimal: ...
    
    async def aplicar(
        self,
        alumno_id: int,
        monto_descuento: Decimal,
        tipo: str,
        motivo: str
    ) -> int: ...


class ICalculadorProrrateo(Protocol):
    """Puerto: Servicio de cálculo de prorrateo."""
    
    async def calcular(
        self,
        monto_total: Decimal,
        fecha_inicio: date,
        fecha_fin: date,
        tipo_periodo: str
    ) -> Dict[str, Any]: ...

    # ========================================
# AGREGADO: Port para Cuotas de Plan de Pago
# ========================================

class ICuotaPlanPagoRepository(Protocol):
    """Port para repositorio de cuotas individuales de planes de pago"""
    
    async def crear(self, cuota: CuotaPlanPagoEntidad) -> CuotaPlanPagoEntidad:
        """Crea una nueva cuota"""
        ...
    
    async def obtener_por_id(self, cuota_id: int) -> Optional[CuotaPlanPagoEntidad]:
        """Obtiene una cuota por ID"""
        ...
    
    async def listar_por_plan(self, plan_id: int) -> List[CuotaPlanPagoEntidad]:
        """Lista todas las cuotas de un plan de pago"""
        ...
    
    async def listar_vencidas(
        self,
        sede_id: int,
        fecha_corte: Optional[date] = None
    ) -> List[CuotaPlanPagoEntidad]:
        """Lista cuotas vencidas hasta una fecha"""
        ...
    
    async def actualizar(self, cuota: CuotaPlanPagoEntidad) -> CuotaPlanPagoEntidad:
        """Actualiza una cuota existente"""
        ...
    
    async def actualizar_masivo(self, cuotas: List[CuotaPlanPagoEntidad]) -> List[CuotaPlanPagoEntidad]:
        """Actualiza múltiples cuotas en batch"""
        ...
    
    async def eliminar(self, cuota_id: int) -> bool:
        """Elimina lógicamente una cuota"""
        ...
    
    

# app/kernel/domain/finanzas/ports.py
"""
Puertos (interfaces) para el módulo de Finanzas.
Define los contratos que deben implementar los repositorios.
"""
from abc import ABC, abstractmethod
from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional, Tuple

from .categoria_pago_entidad import CategoriaPago
from .categoria_egreso_entidad import CategoriaEgreso
from .libro_caja_entidad import LibroCaja, TipoMovimiento
from .pago_entidad import Pago
from .comprobante_entidad import Comprobante
from .arqueo_entidad import ArqueoCaja
from .conciliacion_entidad import Conciliacion
from .libro_caja_entidad import LibroCaja, TipoMovimiento


# ==========================================
# Repositorio: Categorías de Pago
# ==========================================
class CategoriaPagoRepositoryPort(ABC):
    """Puerto para repositorio de categorías de pago"""

    @abstractmethod
    async def crear(self, categoria: CategoriaPago) -> CategoriaPago:
        """Crea una nueva categoría de pago"""
        pass

    @abstractmethod
    async def obtener_por_id(self, categoria_id: int) -> Optional[CategoriaPago]:
        """Obtiene una categoría por ID"""
        pass

    @abstractmethod
    async def listar_por_sede(
        self, 
        sede_id: int, 
        solo_activas: bool = True
    ) -> List[CategoriaPago]:
        """Lista categorías de pago de una sede"""
        pass

    @abstractmethod
    async def actualizar(self, categoria: CategoriaPago) -> CategoriaPago:
        """Actualiza una categoría de pago"""
        pass

    @abstractmethod
    async def existe_nombre_en_sede(
        self, 
        sede_id: int, 
        nombre: str, 
        excluir_id: Optional[int] = None
    ) -> bool:
        """Verifica si existe una categoría con ese nombre en la sede"""
        pass


# ==========================================
# Repositorio: Categorías de Egreso
# ==========================================
class CategoriaEgresoRepositoryPort(ABC):
    """Puerto para repositorio de categorías de egreso"""

    @abstractmethod
    async def crear(self, categoria: CategoriaEgreso) -> CategoriaEgreso:
        """Crea una nueva categoría de egreso"""
        pass

    @abstractmethod
    async def obtener_por_id(self, categoria_id: int) -> Optional[CategoriaEgreso]:
        """Obtiene una categoría por ID"""
        pass

    @abstractmethod
    async def listar_por_sede(
        self, 
        sede_id: int, 
        solo_activas: bool = True
    ) -> List[CategoriaEgreso]:
        """Lista categorías de egreso de una sede"""
        pass

    @abstractmethod
    async def actualizar(self, categoria: CategoriaEgreso) -> CategoriaEgreso:
        """Actualiza una categoría de egreso"""
        pass

    @abstractmethod
    async def existe_nombre_en_sede(
        self, 
        sede_id: int, 
        nombre: str, 
        excluir_id: Optional[int] = None
    ) -> bool:
        """Verifica si existe una categoría con ese nombre en la sede"""
        pass


# ==========================================
# Repositorio: Libro de Caja
# ==========================================
class LibroCajaRepositoryPort(ABC):
    """Puerto para repositorio de libro de caja"""

    @abstractmethod
    async def registrar_movimiento(self, movimiento: LibroCaja) -> LibroCaja:
        """Registra un movimiento en el libro de caja"""
        pass

    @abstractmethod
    async def obtener_por_id(self, movimiento_id: int) -> Optional[LibroCaja]:
        """Obtiene un movimiento por ID"""
        pass

    @abstractmethod
    async def listar_por_sede_y_periodo(
        self,
        sede_id: int,
        fecha_inicio: date,
        fecha_fin: date,
        tipo: Optional[TipoMovimiento] = None
    ) -> List[LibroCaja]:
        """Lista movimientos de una sede en un período"""
        pass

    @abstractmethod
    async def obtener_saldo_actual(self, sede_id: int) -> Decimal:
        """Obtiene el saldo actual de una sede"""
        pass

    @abstractmethod
    async def calcular_totales_periodo(
        self,
        sede_id: int,
        fecha_inicio: date,
        fecha_fin: date
    ) -> Tuple[Decimal, Decimal, Decimal]:
        """
        Calcula totales de un período.
        Retorna: (total_ingresos, total_egresos, saldo_final)
        """
        pass

    @abstractmethod
    async def listar_por_categoria(
        self,
        sede_id: int,
        categoria_id: int,
        tipo: TipoMovimiento,
        fecha_inicio: date,
        fecha_fin: date
    ) -> List[LibroCaja]:
        """Lista movimientos de una categoría específica"""
        pass


# ==========================================
# Repositorio: Pagos
# ==========================================
class PagoRepositoryPort(ABC):
    """Puerto para repositorio de pagos"""

    @abstractmethod
    async def crear(self, pago: Pago) -> Pago:
        """Registra un nuevo pago"""
        pass

    @abstractmethod
    async def obtener_por_id(self, pago_id: int) -> Optional[Pago]:
        """Obtiene un pago por ID"""
        pass

    @abstractmethod
    async def listar_por_sede_y_periodo(
        self,
        sede_id: int,
        fecha_inicio: date,
        fecha_fin: date
    ) -> List[Pago]:
        """Lista pagos de una sede en un período"""
        pass

    @abstractmethod
    async def listar_por_categoria(
        self,
        sede_id: int,
        categoria_id: int,
        fecha_inicio: date,
        fecha_fin: date
    ) -> List[Pago]:
        """Lista pagos de una categoría específica"""
        pass

    @abstractmethod
    async def existe_comprobante(self, comprobante_id: int) -> bool:
        """Verifica si ya existe un pago con ese comprobante"""
        pass


# ==========================================
# Repositorio: Comprobantes
# ==========================================
class ComprobanteRepositoryPort(ABC):
    """Puerto para repositorio de comprobantes"""

    @abstractmethod
    async def crear(self, comprobante: Comprobante) -> Comprobante:
        """Crea un nuevo comprobante"""
        pass

    @abstractmethod
    async def obtener_por_id(self, comprobante_id: int) -> Optional[Comprobante]:
        """Obtiene un comprobante por ID"""
        pass

    @abstractmethod
    async def obtener_por_hash(self, hash_comprobante: str) -> Optional[Comprobante]:
        """Obtiene un comprobante por su hash"""
        pass

    @abstractmethod
    async def existe_hash(self, hash_comprobante: str) -> bool:
        """Verifica si existe un comprobante con ese hash"""
        pass


# ==========================================
# Repositorio: Arqueos
# ==========================================
class ArqueoRepositoryPort(ABC):
    """Puerto para repositorio de arqueos de caja"""

    @abstractmethod
    async def crear(self, arqueo: ArqueoCaja) -> ArqueoCaja:
        """Crea un nuevo arqueo"""
        pass

    @abstractmethod
    async def obtener_por_id(self, arqueo_id: int) -> Optional[ArqueoCaja]:
        """Obtiene un arqueo por ID"""
        pass

    @abstractmethod
    async def obtener_por_sede_y_periodo(
        self,
        sede_id: int,
        periodo_inicio: date,
        periodo_fin: date
    ) -> Optional[ArqueoCaja]:
        """Obtiene el arqueo de una sede para un período específico"""
        pass

    @abstractmethod
    async def listar_por_sede(
        self,
        sede_id: int,
        limite: Optional[int] = None
    ) -> List[ArqueoCaja]:
        """Lista arqueos de una sede (ordenados por fecha desc)"""
        pass

    @abstractmethod
    async def actualizar(self, arqueo: ArqueoCaja) -> ArqueoCaja:
        """Actualiza un arqueo (para recalcular)"""
        pass

    @abstractmethod
    async def existe_para_periodo(
        self,
        sede_id: int,
        periodo_inicio: date,
        periodo_fin: date
    ) -> bool:
        """Verifica si ya existe un arqueo para el período"""
        pass


# ==========================================
# Repositorio: Conciliaciones
# ==========================================
class ConciliacionRepositoryPort(ABC):
    """Puerto para repositorio de conciliaciones bancarias"""

    @abstractmethod
    async def crear(self, conciliacion: Conciliacion) -> Conciliacion:
        """Crea una nueva conciliación"""
        pass

    @abstractmethod
    async def obtener_por_id(self, conciliacion_id: int) -> Optional[Conciliacion]:
        """Obtiene una conciliación por ID"""
        pass

    @abstractmethod
    async def listar_por_sede(
        self,
        sede_id: int,
        fecha_inicio: Optional[date] = None,
        fecha_fin: Optional[date] = None
    ) -> List[Conciliacion]:
        """Lista conciliaciones de una sede"""
        pass

    @abstractmethod
    async def actualizar(self, conciliacion: Conciliacion) -> Conciliacion:
        """Actualiza una conciliación"""
        pass


    @abstractmethod
    async def existe_egreso_por_pago(self, pago_id: int) -> bool:
        """Retorna True si existe un EGRESO en libro_caja con pago_id dado (reversa de pago)."""
        pass

    @abstractmethod
    async def existe_movimiento_por_referencia(self, sede_id: int, referencia: str) -> bool:
        """Retorna True si existe un movimiento con esa referencia en la sede (idempotencia)."""
        pass

class LibroCajaRepositoryPort(ABC):
    @abstractmethod
    async def registrar_movimiento(self, movimiento: LibroCaja) -> LibroCaja: ...
    @abstractmethod
    async def obtener_por_id(self, movimiento_id: int) -> Optional[LibroCaja]: ...
    @abstractmethod
    async def listar_por_sede_y_periodo(
        self, sede_id: int, fecha_inicio: date, fecha_fin: date, tipo: Optional[TipoMovimiento] = None
    ) -> List[LibroCaja]: ...
    @abstractmethod
    async def obtener_saldo_actual(self, sede_id: int) -> Decimal: ...
    @abstractmethod
    async def calcular_totales_periodo(
        self, sede_id: int, fecha_inicio: date, fecha_fin: date
    ) -> Tuple[Decimal, Decimal, Decimal]: ...
    @abstractmethod
    async def existe_egreso_por_pago(self, pago_id: int) -> bool: ...
    @abstractmethod
    async def existe_movimiento_por_referencia(self, sede_id: int, referencia: str) -> bool: ...

class PagoRepositoryPort(ABC):
    @abstractmethod
    async def crear(self, pago: Pago) -> Pago: ...
    @abstractmethod
    async def obtener_por_id(self, pago_id: int) -> Optional[Pago]: ...
    @abstractmethod
    async def listar_por_sede_y_periodo(
        self, sede_id: int, fecha_inicio: Optional[date], fecha_fin: Optional[date]
    ) -> List[Pago]: ...
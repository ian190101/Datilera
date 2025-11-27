# app/kernel/domain/cursosextra/ports.py

"""
Puertos (interfaces) para el módulo de Cursos Extra.
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional, Dict

from .curso_extra_entidad import CursoExtra
from .inscripcion_curso_extra_entidad import (
    InscripcionCursoExtra,
    TipoAlumnoCursoExtra,
    EstadoInscripcionCursoExtra
)
from .alumno_externo_entidad import AlumnoExterno
from .balance_curso_extra_entidad import BalanceCursoExtra, EstadoBalance
from .pago_curso_extra_entidad import PagoCursoExtra, MetodoPagoCursoExtra
from .costo_curso_extra_entidad import CostoCursoExtra
from .categoria_costo_curso_extra_entidad import CategoriaCostoCursoExtra
from .ingreso_curso_extra_entidad import IngresoCursoExtra


# ==========================
# Repositorio: Cursos Extra
# ==========================

class CursoExtraRepositoryPort(ABC):
    """Puerto para repositorio de cursos extra."""
    
    @abstractmethod
    async def crear(self, curso: CursoExtra) -> CursoExtra:
        """Crea un nuevo curso extra."""
        raise NotImplementedError
    
    @abstractmethod
    async def obtener_por_id(self, curso_id: int) -> Optional[CursoExtra]:
        """Obtiene un curso por su ID."""
        raise NotImplementedError
    
    @abstractmethod
    async def obtener_por_sede(
        self,
        sede_id: int,
        activo: Optional[bool] = None,
        gestion: Optional[int] = None,
        limite: int = 100,
        offset: int = 0
    ) -> List[CursoExtra]:
        """Lista cursos de una sede con filtros opcionales."""
        raise NotImplementedError
    
    @abstractmethod
    async def guardar(self, curso: CursoExtra) -> CursoExtra:
        """Persiste cambios del curso."""
        raise NotImplementedError
    
    @abstractmethod
    async def activar_desactivar(self, curso_id: int, activo: bool) -> CursoExtra:
        """Activa o desactiva un curso."""
        raise NotImplementedError
    
    @abstractmethod
    async def incrementar_inscritos(self, curso_id: int) -> CursoExtra:
        """Incrementa el contador de inscritos actuales."""
        raise NotImplementedError
    
    @abstractmethod
    async def decrementar_inscritos(self, curso_id: int) -> CursoExtra:
        """Decrementa el contador de inscritos actuales."""
        raise NotImplementedError
    
    @abstractmethod
    async def verificar_cupos_disponibles(self, curso_id: int) -> bool:
        """Verifica si hay cupos disponibles."""
        raise NotImplementedError
    
    @abstractmethod
    async def buscar_por_nombre(
        self,
        nombre: str,
        sede_id: Optional[int] = None,
        limite: int = 20
    ) -> List[CursoExtra]:
        """Busca cursos por nombre (búsqueda parcial)."""
        raise NotImplementedError
    
    @abstractmethod
    async def obtener_por_instructor(
        self,
        instructor: str,
        sede_id: Optional[int] = None
    ) -> List[CursoExtra]:
        """Lista cursos por instructor."""
        raise NotImplementedError
    
    @abstractmethod
    async def obtener_activos_con_cupos(self, sede_id: int) -> List[CursoExtra]:
        """Obtiene cursos activos que aún tienen cupos disponibles."""
        raise NotImplementedError


# ==========================
# Repositorio: Inscripciones
# ==========================

class InscripcionCursoExtraRepositoryPort(ABC):
    """Puerto para repositorio de inscripciones a cursos extra."""
    
    @abstractmethod
    async def crear(self, inscripcion: InscripcionCursoExtra) -> InscripcionCursoExtra:
        """Crea una nueva inscripción."""
        raise NotImplementedError
    
    @abstractmethod
    async def obtener_por_id(self, inscripcion_id: int) -> Optional[InscripcionCursoExtra]:
        """Obtiene una inscripción por su ID."""
        raise NotImplementedError
    
    @abstractmethod
    async def obtener_por_curso(
        self,
        curso_id: int,
        estado: Optional[EstadoInscripcionCursoExtra] = None,
        limite: int = 100,
        offset: int = 0
    ) -> List[InscripcionCursoExtra]:
        """Lista inscripciones de un curso."""
        raise NotImplementedError
    
    @abstractmethod
    async def obtener_por_alumno_interno(
        self,
        alumno_id: int,
        estado: Optional[EstadoInscripcionCursoExtra] = None
    ) -> List[InscripcionCursoExtra]:
        """Lista inscripciones de un alumno interno."""
        raise NotImplementedError
    
    @abstractmethod
    async def obtener_por_alumno_externo(
        self,
        alumno_externo_id: int,
        estado: Optional[EstadoInscripcionCursoExtra] = None
    ) -> List[InscripcionCursoExtra]:
        """Lista inscripciones de un alumno externo."""
        raise NotImplementedError
    
    @abstractmethod
    async def guardar(self, inscripcion: InscripcionCursoExtra) -> InscripcionCursoExtra:
        """Persiste cambios de la inscripción."""
        raise NotImplementedError
    
    @abstractmethod
    async def actualizar_estado(
        self,
        inscripcion_id: int,
        estado: EstadoInscripcionCursoExtra
    ) -> InscripcionCursoExtra:
        """Actualiza el estado de una inscripción."""
        raise NotImplementedError
    
    @abstractmethod
    async def existe_inscripcion_activa(
        self,
        curso_id: int,
        alumno_id: Optional[int] = None,
        alumno_externo_id: Optional[int] = None
    ) -> bool:
        """Verifica si existe una inscripción activa."""
        raise NotImplementedError
    
    @abstractmethod
    async def contar_inscritos_activos(self, curso_id: int) -> int:
        """Cuenta inscripciones activas de un curso."""
        raise NotImplementedError
    
    @abstractmethod
    async def contar_por_tipo(
        self,
        curso_id: int,
        tipo: TipoAlumnoCursoExtra
    ) -> int:
        """Cuenta inscripciones por tipo (internos/externos)."""
        raise NotImplementedError


# ==========================
# Repositorio: Alumnos Externos
# ==========================

class AlumnoExternoRepositoryPort(ABC):
    """Puerto para repositorio de alumnos externos."""
    
    @abstractmethod
    async def crear(self, alumno: AlumnoExterno) -> AlumnoExterno:
        """Crea un nuevo alumno externo."""
        raise NotImplementedError
    
    @abstractmethod
    async def obtener_por_id(self, alumno_id: int) -> Optional[AlumnoExterno]:
        """Obtiene un alumno externo por su ID."""
        raise NotImplementedError
    
    @abstractmethod
    async def obtener_por_sede(
        self,
        sede_id: int,
        limite: int = 100,
        offset: int = 0
    ) -> List[AlumnoExterno]:
        """Lista alumnos externos de una sede."""
        raise NotImplementedError
    
    @abstractmethod
    async def guardar(self, alumno: AlumnoExterno) -> AlumnoExterno:
        """Persiste cambios del alumno externo."""
        raise NotImplementedError
    
    @abstractmethod
    async def buscar_por_nombre(
        self,
        nombre: str,
        sede_id: Optional[int] = None,
        limite: int = 20
    ) -> List[AlumnoExterno]:
        """Busca alumnos externos por nombre."""
        raise NotImplementedError
    
    @abstractmethod
    async def buscar_por_celular_tutor(
        self,
        celular: str,
        sede_id: Optional[int] = None
    ) -> List[AlumnoExterno]:
        """Busca alumnos externos por celular del tutor."""
        raise NotImplementedError
    
    @abstractmethod
    async def existe_por_nombre_y_tutor(
        self,
        nombre_completo: str,
        tutor_celular: str,
        sede_id: int
    ) -> bool:
        """Verifica si existe un alumno externo con ese nombre y tutor."""
        raise NotImplementedError


# ==========================
# Repositorio: Balance
# ==========================

class BalanceCursoExtraRepositoryPort(ABC):
    """Puerto para repositorio de balance de cursos extra."""
    
    @abstractmethod
    async def crear(self, balance: BalanceCursoExtra) -> BalanceCursoExtra:
        """Crea un balance para una inscripción."""
        raise NotImplementedError
    
    @abstractmethod
    async def obtener_por_id(self, balance_id: int) -> Optional[BalanceCursoExtra]:
        """Obtiene un balance por su ID."""
        raise NotImplementedError
    
    @abstractmethod
    async def obtener_por_inscripcion(
        self,
        inscripcion_id: int
    ) -> Optional[BalanceCursoExtra]:
        """Obtiene el balance de una inscripción."""
        raise NotImplementedError
    
    @abstractmethod
    async def guardar(self, balance: BalanceCursoExtra) -> BalanceCursoExtra:
        """Persiste cambios del balance."""
        raise NotImplementedError
    
    @abstractmethod
    async def actualizar_montos(
        self,
        balance_id: int,
        monto_pagado: Decimal,
        saldo: Decimal,
        estado: EstadoBalance
    ) -> BalanceCursoExtra:
        """Actualiza los montos del balance tras un pago."""
        raise NotImplementedError
    
    @abstractmethod
    async def listar_pendientes_por_curso(
        self,
        curso_id: int
    ) -> List[BalanceCursoExtra]:
        """Lista balances pendientes o parciales de un curso."""
        raise NotImplementedError
    
    @abstractmethod
    async def calcular_total_pendiente(self, curso_id: int) -> Decimal:
        """Suma el total de saldos pendientes de un curso."""
        raise NotImplementedError
    
    @abstractmethod
    async def calcular_total_pagado(self, curso_id: int) -> Decimal:
        """Suma el total de montos pagados de un curso."""
        raise NotImplementedError


# ==========================
# Repositorio: Pagos
# ==========================

class PagoCursoExtraRepositoryPort(ABC):
    """Puerto para repositorio de pagos de cursos extra."""
    
    @abstractmethod
    async def crear(self, pago: PagoCursoExtra) -> PagoCursoExtra:
        """Registra un nuevo pago."""
        raise NotImplementedError
    
    @abstractmethod
    async def obtener_por_id(self, pago_id: int) -> Optional[PagoCursoExtra]:
        """Obtiene un pago por su ID."""
        raise NotImplementedError
    
    @abstractmethod
    async def listar_por_balance(
        self,
        balance_id: int
    ) -> List[PagoCursoExtra]:
        """Lista todos los pagos de un balance."""
        raise NotImplementedError
    
    @abstractmethod
    async def listar_por_curso(
        self,
        curso_id: int,
        fecha_desde: Optional[date] = None,
        fecha_hasta: Optional[date] = None,
        limite: int = 100,
        offset: int = 0
    ) -> List[PagoCursoExtra]:
        """Lista pagos de un curso con filtro de fechas opcional."""
        raise NotImplementedError
    
    @abstractmethod
    async def calcular_total_por_balance(self, balance_id: int) -> Decimal:
        """Suma el total de pagos de un balance."""
        raise NotImplementedError
    
    @abstractmethod
    async def calcular_total_por_curso(
        self,
        curso_id: int,
        fecha_desde: Optional[date] = None,
        fecha_hasta: Optional[date] = None
    ) -> Decimal:
        """Suma el total de pagos de un curso."""
        raise NotImplementedError


# ==========================
# Repositorio: Costos
# ==========================

class CostoCursoExtraRepositoryPort(ABC):
    """Puerto para repositorio de costos de cursos extra."""
    
    @abstractmethod
    async def crear(self, costo: CostoCursoExtra) -> CostoCursoExtra:
        """Registra un nuevo costo."""
        raise NotImplementedError
    
    @abstractmethod
    async def obtener_por_id(self, costo_id: int) -> Optional[CostoCursoExtra]:
        """Obtiene un costo por su ID."""
        raise NotImplementedError
    
    @abstractmethod
    async def listar_por_curso(
        self,
        curso_id: int,
        fecha_desde: Optional[datetime] = None,
        fecha_hasta: Optional[datetime] = None,
        limite: int = 100,
        offset: int = 0
    ) -> List[CostoCursoExtra]:
        """Lista costos de un curso."""
        raise NotImplementedError
    
    @abstractmethod
    async def guardar(self, costo: CostoCursoExtra) -> CostoCursoExtra:
        """Persiste cambios del costo."""
        raise NotImplementedError
    
    @abstractmethod
    async def eliminar(self, costo_id: int) -> bool:
        """Elimina un costo."""
        raise NotImplementedError
    
    @abstractmethod
    async def calcular_total_por_curso(self, curso_id: int) -> Decimal:
        """Suma el total de costos de un curso."""
        raise NotImplementedError
    
    @abstractmethod
    async def calcular_total_por_categoria(
        self,
        curso_id: int,
        categoria_id: int
    ) -> Decimal:
        """Suma costos por categoría en un curso."""
        raise NotImplementedError


# ==========================
# Repositorio: Categorías de Costo
# ==========================

class CategoriaCostoCursoExtraRepositoryPort(ABC):
    """Puerto para repositorio de categorías de costo."""
    
    @abstractmethod
    async def crear(self, categoria: CategoriaCostoCursoExtra) -> CategoriaCostoCursoExtra:
        """Crea una nueva categoría de costo."""
        raise NotImplementedError
    
    @abstractmethod
    async def obtener_por_id(self, categoria_id: int) -> Optional[CategoriaCostoCursoExtra]:
        """Obtiene una categoría por su ID."""
        raise NotImplementedError
    
    @abstractmethod
    async def listar_por_curso(
        self,
        curso_id: int,
        activo: Optional[bool] = None
    ) -> List[CategoriaCostoCursoExtra]:
        """Lista categorías de un curso."""
        raise NotImplementedError
    
    @abstractmethod
    async def guardar(self, categoria: CategoriaCostoCursoExtra) -> CategoriaCostoCursoExtra:
        """Persiste cambios de la categoría."""
        raise NotImplementedError
    
    @abstractmethod
    async def activar_desactivar(
        self,
        categoria_id: int,
        activo: bool
    ) -> CategoriaCostoCursoExtra:
        """Activa o desactiva una categoría."""
        raise NotImplementedError
    
    @abstractmethod
    async def eliminar(self, categoria_id: int) -> bool:
        """Elimina una categoría (solo si no tiene costos asociados)."""
        raise NotImplementedError
    
    @abstractmethod
    async def existe_por_nombre(
        self,
        nombre: str,
        curso_id: int,
        excluir_id: Optional[int] = None
    ) -> bool:
        """Verifica si existe una categoría con ese nombre en el curso."""
        raise NotImplementedError


# ==========================
# Repositorio: Ingresos Consolidados
# ==========================

class IngresoCursoExtraRepositoryPort(ABC):
    """Puerto para repositorio de ingresos consolidados."""
    
    @abstractmethod
    async def crear(self, ingreso: IngresoCursoExtra) -> IngresoCursoExtra:
        """Crea el registro de ingresos para un curso."""
        raise NotImplementedError
    
    @abstractmethod
    async def obtener_por_curso(self, curso_id: int) -> Optional[IngresoCursoExtra]:
        """Obtiene el registro de ingresos de un curso."""
        raise NotImplementedError
    
    @abstractmethod
    async def guardar(self, ingreso: IngresoCursoExtra) -> IngresoCursoExtra:
        """Persiste cambios del registro de ingresos."""
        raise NotImplementedError
    
    @abstractmethod
    async def actualizar_ingresos(
        self,
        curso_id: int,
        total_ingresos: Decimal
    ) -> IngresoCursoExtra:
        """Actualiza el total de ingresos."""
        raise NotImplementedError
    
    @abstractmethod
    async def actualizar_gastos(
        self,
        curso_id: int,
        total_gastos: Decimal
    ) -> IngresoCursoExtra:
        """Actualiza el total de gastos."""
        raise NotImplementedError
    
    @abstractmethod
    async def recalcular_ganancias(self, curso_id: int) -> IngresoCursoExtra:
        """Recalcula ganancia_bruta, ganancia_institucion y ganancia_instructor."""
        raise NotImplementedError
    
    @abstractmethod
    async def obtener_balance_curso(self, curso_id: int) -> Dict:
        """
        Retorna un diccionario con el balance completo del curso:
        {
            'total_ingresos': Decimal,
            'total_gastos': Decimal,
            'ganancia_bruta': Decimal,
            'ganancia_institucion': Decimal,
            'ganancia_instructor': Decimal,
            'porcentaje_institucion': Decimal
        }
        """
        raise NotImplementedError

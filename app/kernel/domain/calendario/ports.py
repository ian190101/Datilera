# app/kernel/domain/calendario/ports.py

from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import date

# Imports desde el mismo nivel (entities están al mismo nivel que ports.py)
from .tipo_evento_entidad import TipoEvento
from .evento_calendario_entidad import EventoCalendario
from .planificacion_actividad_entidad import PlanificacionActividad


# =========================================================================
# PORT: TIPOS DE EVENTOS
# =========================================================================

class TipoEventoRepositoryPort(ABC):
    """Puerto: Repositorio de tipos de eventos."""
    
    @abstractmethod
    async def crear(self, tipo: TipoEvento) -> TipoEvento:
        """Crea un nuevo tipo de evento."""
        pass
    
    @abstractmethod
    async def obtener(self, tipo_id: int) -> Optional[TipoEvento]:
        """Obtiene un tipo de evento por ID."""
        pass
    
    @abstractmethod
    async def listar(
        self,
        sede_id: Optional[int] = None,
        activo: Optional[bool] = None,
    ) -> List[TipoEvento]:
        """Lista tipos de eventos."""
        pass
    
    @abstractmethod
    async def actualizar(self, tipo: TipoEvento) -> TipoEvento:
        """Actualiza un tipo de evento existente."""
        pass
    
    @abstractmethod
    async def activar_desactivar(self, tipo_id: int, activo: bool) -> TipoEvento:
        """Activa o desactiva un tipo de evento."""
        pass


# =========================================================================
# PORT: EVENTOS DEL CALENDARIO
# =========================================================================

class EventoCalendarioRepositoryPort(ABC):
    """Puerto: Repositorio de eventos del calendario."""
    
    @abstractmethod
    async def crear(self, evento: EventoCalendario) -> EventoCalendario:
        """Crea un nuevo evento."""
        pass
    
    @abstractmethod
    async def obtener(self, evento_id: int) -> Optional[EventoCalendario]:
        """Obtiene un evento por ID."""
        pass
    
    @abstractmethod
    async def listar(
        self,
        sede_id: Optional[int] = None,
        fecha_inicio: Optional[date] = None,
        fecha_fin: Optional[date] = None,
        tipo_evento_id: Optional[int] = None,
        aprobado: Optional[bool] = None,
        limite: int = 100,
        offset: int = 0,
    ) -> List[EventoCalendario]:
        """Lista eventos con filtros."""
        pass
    
    @abstractmethod
    async def actualizar(self, evento: EventoCalendario) -> EventoCalendario:
        """Actualiza un evento existente."""
        pass
    
    @abstractmethod
    async def eliminar(self, evento_id: int) -> bool:
        """Elimina un evento."""
        pass
    
    # ✅ MÉTODO QUE FALTABA
    @abstractmethod
    async def obtener_eventos_con_recordatorio_pendiente(
        self,
        fecha_actual: date
    ) -> List[EventoCalendario]:
        """Obtiene eventos que necesitan enviar recordatorio.
        
        Args:
            fecha_actual: Fecha actual para calcular días restantes
            
        Returns:
            Lista de eventos con recordatorio pendiente
        """
        pass
    
    # ✅ MÉTODO ADICIONAL (para aprobar eventos)
    @abstractmethod
    async def obtener_eventos_pendientes_aprobacion(
        self,
        sede_id: int
    ) -> List[EventoCalendario]:
        """Obtiene eventos pendientes de aprobación de una sede.
        
        Args:
            sede_id: ID de la sede
            
        Returns:
            Lista de eventos pendientes de aprobación
        """
        pass


# =========================================================================
# PORT: PLANIFICACIONES DE ACTIVIDADES
# =========================================================================

class PlanificacionActividadRepositoryPort(ABC):
    """Puerto: Repositorio de planificaciones de actividades."""
    
    @abstractmethod
    async def crear(self, planificacion: PlanificacionActividad) -> PlanificacionActividad:
        """Crea una nueva planificación."""
        pass
    
    @abstractmethod
    async def obtener(self, planificacion_id: int) -> Optional[PlanificacionActividad]:
        """Obtiene una planificación por ID."""
        pass
    
    @abstractmethod
    async def listar_por_fecha(
        self,
        fecha: date,
        sede_id: Optional[int] = None,
        profesora_id: Optional[int] = None,
        paralelo_id: Optional[int] = None,
    ) -> List[PlanificacionActividad]:
        """Lista planificaciones de una fecha específica."""
        pass
    
    @abstractmethod
    async def listar_por_rango(
        self,
        fecha_inicio: date,
        fecha_fin: date,
        sede_id: Optional[int] = None,
        profesora_id: Optional[int] = None,
    ) -> List[PlanificacionActividad]:
        """Lista planificaciones en un rango de fechas."""
        pass
    
    @abstractmethod
    async def actualizar(self, planificacion: PlanificacionActividad) -> PlanificacionActividad:
        """Actualiza una planificación existente."""
        pass
    
    @abstractmethod
    async def eliminar(self, planificacion_id: int) -> bool:
        """Elimina una planificación."""
        pass
    
    # ✅ MÉTODO QUE FALTABA
    @abstractmethod
    async def obtener_planificaciones_pendientes(
        self,
        fecha_limite: date,
        sede_id: Optional[int] = None
    ) -> List[PlanificacionActividad]:
        """Obtiene planificaciones no completadas hasta una fecha.
        
        Args:
            fecha_limite: Fecha límite
            sede_id: Filtrar por sede (opcional)
            
        Returns:
            Lista de planificaciones pendientes (no completadas)
        """
        pass

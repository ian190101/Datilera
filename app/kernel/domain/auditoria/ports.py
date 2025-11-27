# app/kernel/domain/auditoria/ports.py

"""
Puertos (Interfaces) del Dominio de Auditoría.

Define los contratos que debe cumplir la infraestructura.
NO depende de implementaciones concretas.
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Sequence, Optional, Dict, List, Any

# NO importar modelos SQLAlchemy aquí
# Solo trabajar con tipos primitivos y estructuras de datos básicas


# ===========================================================================
# Puerto: Auditoría de Acciones
# ===========================================================================

class AuditoriaAccionRepositoryPort(ABC):
    """
    Puerto para repositorio de auditoría de acciones.
    
    Los métodos reciben/retornan tipos primitivos y modelos SQLAlchemy.
    El mapeo a entidades de dominio se hace en la capa de aplicación.
    """
    
    @abstractmethod
    async def registrar(
        self,
        usuario_id: Optional[int],
        sede_id: Optional[int],
        entidad: str,
        accion: str,
        *,
        entidad_id: Optional[str] = None,
        datos_antes: Optional[Dict[str, Any]] = None,
        datos_despues: Optional[Dict[str, Any]] = None,
        ip: Optional[str] = None,
        user_agent: Optional[str] = None,
        sesion_id: Optional[int] = None,
        nivel: str = "info",
        metodo_http: Optional[str] = None,
        endpoint: Optional[str] = None,
        codigo_respuesta: Optional[int] = None,
        duracion_ms: Optional[int] = None,
        descripcion: Optional[str] = None,
        tags: Optional[List[str]] = None,
        contexto: Optional[Dict[str, Any]] = None,
        exitoso: bool = True,
        mensaje_error: Optional[str] = None,
        stack_trace: Optional[str] = None,
        dispositivo_info: Optional[Dict[str, Any]] = None,
        geolocalizacion: Optional[Dict[str, Any]] = None,
    ):
        """Registra un evento de auditoría."""
        raise NotImplementedError
    
    @abstractmethod
    async def listar_por_usuario(
        self,
        usuario_id: int,
        *,
        limit: int = 100,
        offset: int = 0
    ):
        """Lista eventos por usuario."""
        raise NotImplementedError
    
    @abstractmethod
    async def listar_por_sede(
        self,
        sede_id: int,
        *,
        desde: Optional[datetime] = None,
        hasta: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0
    ):
        """Lista eventos por sede."""
        raise NotImplementedError
    
    @abstractmethod
    async def listar_por_entidad(
        self,
        entidad: str,
        *,
        entidad_id: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ):
        """Lista eventos por entidad."""
        raise NotImplementedError
    
    @abstractmethod
    async def listar_por_accion(
        self,
        accion: str,
        *,
        limit: int = 100,
        offset: int = 0
    ):
        """Lista eventos por tipo de acción."""
        raise NotImplementedError
    
    @abstractmethod
    async def listar_por_nivel(
        self,
        nivel: str,
        *,
        desde: Optional[datetime] = None,
        hasta: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0
    ):
        """Lista eventos por nivel de severidad."""
        raise NotImplementedError
    
    @abstractmethod
    async def listar_errores(
        self,
        *,
        sede_id: Optional[int] = None,
        desde: Optional[datetime] = None,
        hasta: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0
    ):
        """Lista solo eventos con errores."""
        raise NotImplementedError
    
    @abstractmethod
    async def buscar_por_descripcion(
        self,
        termino: str,
        *,
        sede_id: Optional[int] = None,
        limit: int = 50
    ):
        """Búsqueda de texto en descripción."""
        raise NotImplementedError
    
    @abstractmethod
    async def listar_por_endpoint(
        self,
        endpoint: str,
        *,
        metodo_http: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ):
        """Lista eventos por endpoint."""
        raise NotImplementedError
    
    @abstractmethod
    async def listar_por_ip(
        self,
        ip: str,
        *,
        desde: Optional[datetime] = None,
        hasta: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0
    ):
        """Lista eventos por IP."""
        raise NotImplementedError
    
    @abstractmethod
    async def obtener_por_id(self, auditoria_id: int):
        """Obtiene un evento por ID."""
        raise NotImplementedError
    
    @abstractmethod
    async def contar_por_accion(
        self,
        *,
        sede_id: Optional[int] = None,
        desde: Optional[datetime] = None,
        hasta: Optional[datetime] = None
    ) -> Dict[str, int]:
        """Cuenta eventos agrupados por acción."""
        raise NotImplementedError
    
    @abstractmethod
    async def contar_por_entidad(
        self,
        *,
        sede_id: Optional[int] = None,
        desde: Optional[datetime] = None,
        hasta: Optional[datetime] = None
    ) -> Dict[str, int]:
        """Cuenta eventos agrupados por entidad."""
        raise NotImplementedError
    
    @abstractmethod
    async def contar_errores_por_endpoint(
        self,
        *,
        desde: Optional[datetime] = None,
        hasta: Optional[datetime] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Top N endpoints con más errores."""
        raise NotImplementedError
    
    @abstractmethod
    async def obtener_duracion_promedio_por_endpoint(
        self,
        endpoint: str,
        *,
        desde: Optional[datetime] = None,
        hasta: Optional[datetime] = None
    ) -> Optional[float]:
        """Calcula duración promedio (ms) para un endpoint."""
        raise NotImplementedError
    
    @abstractmethod
    async def obtener_actividad_por_hora(
        self,
        *,
        sede_id: Optional[int] = None,
        fecha: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Obtiene actividad agrupada por hora."""
        raise NotImplementedError
    
    @abstractmethod
    async def obtener_usuarios_mas_activos(
        self,
        *,
        sede_id: Optional[int] = None,
        desde: Optional[datetime] = None,
        hasta: Optional[datetime] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Top N usuarios más activos."""
        raise NotImplementedError
    
    @abstractmethod
    async def limpiar_antiguos(self, dias: int = 90) -> int:
        """Limpia eventos antiguos."""
        raise NotImplementedError


# ===========================================================================
# Puerto: Auditoría de Sesiones
# ===========================================================================

class AuditoriaSesionRepositoryPort(ABC):
    """Puerto para repositorio de sesiones activas."""
    
    @abstractmethod
    async def registrar_inicio(
        self,
        sesion_id: int,
        usuario_id: int,
        sede_id: Optional[int],
        ip: Optional[str],
        user_agent: Optional[str],
        dispositivo_tipo: Optional[str],
    ):
        """Registra inicio de sesión."""
        raise NotImplementedError
    
    @abstractmethod
    async def actualizar_heartbeat(self, sesion_id: int) -> None:
        """Actualiza timestamp de última actividad."""
        raise NotImplementedError
    
    @abstractmethod
    async def registrar_cierre(
        self,
        sesion_id: int,
        razon: str = "logout_manual"
    ) -> None:
        """Registra cierre de sesión."""
        raise NotImplementedError
    
    @abstractmethod
    async def listar_activas(
        self,
        *,
        sede_id: Optional[int] = None,
        usuario_id: Optional[int] = None
    ):
        """Lista sesiones activas."""
        raise NotImplementedError
    
    @abstractmethod
    async def obtener_por_sesion_id(self, sesion_id: int):
        """Obtiene una sesión por su sesion_id."""
        raise NotImplementedError
    
    @abstractmethod
    async def contar_activas_por_usuario(self, usuario_id: int) -> int:
        """Cuenta sesiones activas de un usuario."""
        raise NotImplementedError
    
    @abstractmethod
    async def cerrar_inactivas(self, timeout_minutos: int = 30) -> int:
        """Cierra sesiones inactivas."""
        raise NotImplementedError
    
    @abstractmethod
    async def forzar_cierre_usuario(self, usuario_id: int) -> int:
        """Cierra todas las sesiones activas de un usuario."""
        raise NotImplementedError
    
    @abstractmethod
    async def obtener_duracion_promedio_sesiones(
        self,
        *,
        usuario_id: Optional[int] = None,
        desde: Optional[datetime] = None
    ) -> Optional[float]:
        """Calcula duración promedio de sesiones (en minutos)."""
        raise NotImplementedError


# ===========================================================================
# Puerto: Auditoría de Cambios
# ===========================================================================

class AuditoriaCambioRepositoryPort(ABC):
    """Puerto para repositorio de cambios campo por campo."""
    
    @abstractmethod
    async def registrar(
        self,
        auditoria_accion_id: int,
        campo: str,
        valor_anterior: Optional[str],
        valor_nuevo: Optional[str],
        tipo_dato: Optional[str],
    ):
        """Registra un cambio individual."""
        raise NotImplementedError
    
    @abstractmethod
    async def registrar_multiples(
        self,
        cambios: List[Dict[str, Any]]
    ) -> None:
        """Registra múltiples cambios (bulk insert)."""
        raise NotImplementedError
    
    @abstractmethod
    async def listar_por_accion(
        self,
        auditoria_accion_id: int
    ):
        """Lista todos los cambios de una acción."""
        raise NotImplementedError
    
    @abstractmethod
    async def listar_por_campo(
        self,
        auditoria_accion_id: int,
        campo: str
    ):
        """Obtiene el cambio de un campo específico."""
        raise NotImplementedError


# ===========================================================================
# Puerto: Auditoría de Exportaciones
# ===========================================================================

class AuditoriaExportacionRepositoryPort(ABC):
    """Puerto para repositorio de exportaciones."""
    
    @abstractmethod
    async def registrar(
        self,
        usuario_id: Optional[int],
        sede_id: Optional[int],
        tipo: str,
        formato: str,
        total_registros: int,
        *,
        filtros: Optional[Dict[str, Any]] = None,
        columnas: Optional[List[str]] = None,
        ruta_archivo: Optional[str] = None,
        exitoso: bool = True,
        mensaje_error: Optional[str] = None,
    ):
        """Registra una nueva exportación."""
        raise NotImplementedError
    
    @abstractmethod
    async def marcar_descargado(self, exportacion_id: int) -> None:
        """Marca una exportación como descargada."""
        raise NotImplementedError
    
    @abstractmethod
    async def obtener_por_id(self, exportacion_id: int):
        """Obtiene una exportación por su ID."""
        raise NotImplementedError
    
    @abstractmethod
    async def listar_por_usuario(
        self,
        usuario_id: int,
        *,
        desde: Optional[datetime] = None,
        hasta: Optional[datetime] = None,
        tipo: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ):
        """Lista exportaciones de un usuario."""
        raise NotImplementedError
    
    @abstractmethod
    async def listar_por_sede(
        self,
        sede_id: int,
        *,
        desde: Optional[datetime] = None,
        hasta: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0
    ):
        """Lista exportaciones de una sede."""
        raise NotImplementedError
    
    @abstractmethod
    async def listar_por_tipo(
        self,
        tipo: str,
        *,
        desde: Optional[datetime] = None,
        hasta: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0
    ):
        """Lista exportaciones por tipo."""
        raise NotImplementedError
    
    @abstractmethod
    async def listar_fallidas(
        self,
        *,
        sede_id: Optional[int] = None,
        desde: Optional[datetime] = None,
        limit: int = 50
    ):
        """Lista exportaciones fallidas."""
        raise NotImplementedError
    
    @abstractmethod
    async def contar_por_tipo(
        self,
        *,
        usuario_id: Optional[int] = None,
        sede_id: Optional[int] = None,
        desde: Optional[datetime] = None,
        hasta: Optional[datetime] = None
    ) -> Dict[str, int]:
        """Cuenta exportaciones agrupadas por tipo."""
        raise NotImplementedError
    
    @abstractmethod
    async def contar_por_formato(
        self,
        *,
        tipo: Optional[str] = None,
        desde: Optional[datetime] = None,
        hasta: Optional[datetime] = None
    ) -> Dict[str, int]:
        """Cuenta exportaciones agrupadas por formato."""
        raise NotImplementedError
    
    @abstractmethod
    async def obtener_total_registros_exportados(
        self,
        *,
        usuario_id: Optional[int] = None,
        tipo: Optional[str] = None,
        desde: Optional[datetime] = None,
        hasta: Optional[datetime] = None
    ) -> int:
        """Suma total de registros exportados."""
        raise NotImplementedError
    
    @abstractmethod
    async def detectar_exportaciones_masivas(
        self,
        umbral_registros: int = 1000,
        ventana_horas: int = 1
    ):
        """Detecta exportaciones masivas sospechosas."""
        raise NotImplementedError
    
    @abstractmethod
    async def obtener_exportaciones_por_usuario_periodo(
        self,
        usuario_id: int,
        ventana_horas: int = 24
    ):
        """Obtiene exportaciones de un usuario en las últimas N horas."""
        raise NotImplementedError
    
    @abstractmethod
    async def limpiar_archivos_antiguos(self, dias: int = 7) -> int:
        """Marca para limpieza archivos antiguos."""
        raise NotImplementedError


# ===========================================================================
# Puerto: Auditoría de Prompts IA
# ===========================================================================

class AuditoriaPromptIARepositoryPort(ABC):
    """Puerto para repositorio de consultas a IA."""
    
    @abstractmethod
    async def registrar(
        self,
        usuario_id: Optional[int],
        sede_id: Optional[int],
        prompt_original: str,
        *,
        prompt_sanitizado: Optional[str] = None,
        respuesta: Optional[str] = None,
        tokens_prompt: Optional[int] = None,
        tokens_respuesta: Optional[int] = None,
        tokens_total: Optional[int] = None,
        modelo: Optional[str] = None,
        costo_usd: Optional[str] = None,
        categoria: Optional[str] = None,
        tiene_datos_sensibles: bool = False,
        exitoso: bool = True,
        mensaje_error: Optional[str] = None,
        duracion_segundos: Optional[int] = None,
    ):
        """Registra una consulta a IA."""
        raise NotImplementedError
    
    @abstractmethod
    async def obtener_por_id(self, prompt_id: int):
        """Obtiene un prompt por su ID."""
        raise NotImplementedError
    
    @abstractmethod
    async def listar_por_usuario(
        self,
        usuario_id: int,
        *,
        desde: Optional[datetime] = None,
        hasta: Optional[datetime] = None,
        categoria: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ):
        """Lista prompts de un usuario."""
        raise NotImplementedError
    
    @abstractmethod
    async def listar_por_sede(
        self,
        sede_id: int,
        *,
        desde: Optional[datetime] = None,
        hasta: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0
    ):
        """Lista prompts de una sede."""
        raise NotImplementedError
    
    @abstractmethod
    async def listar_con_datos_sensibles(
        self,
        *,
        sede_id: Optional[int] = None,
        desde: Optional[datetime] = None,
        limit: int = 50
    ):
        """Lista prompts con datos sensibles."""
        raise NotImplementedError
    
    @abstractmethod
    async def listar_fallidos(
        self,
        *,
        usuario_id: Optional[int] = None,
        desde: Optional[datetime] = None,
        limit: int = 50
    ):
        """Lista prompts fallidos."""
        raise NotImplementedError
    
    @abstractmethod
    async def calcular_tokens_consumidos(
        self,
        *,
        usuario_id: Optional[int] = None,
        sede_id: Optional[int] = None,
        desde: Optional[datetime] = None,
        hasta: Optional[datetime] = None
    ) -> Dict[str, int]:
        """Calcula total de tokens consumidos."""
        raise NotImplementedError
    
    @abstractmethod
    async def calcular_costo_total(
        self,
        *,
        usuario_id: Optional[int] = None,
        sede_id: Optional[int] = None,
        desde: Optional[datetime] = None,
        hasta: Optional[datetime] = None
    ) -> float:
        """Calcula costo total en USD."""
        raise NotImplementedError
    
    @abstractmethod
    async def contar_por_categoria(
        self,
        *,
        usuario_id: Optional[int] = None,
        desde: Optional[datetime] = None,
        hasta: Optional[datetime] = None
    ) -> Dict[str, int]:
        """Cuenta prompts por categoría."""
        raise NotImplementedError
    
    @abstractmethod
    async def contar_por_modelo(
        self,
        *,
        desde: Optional[datetime] = None,
        hasta: Optional[datetime] = None
    ) -> Dict[str, int]:
        """Cuenta prompts por modelo."""
        raise NotImplementedError
    
    @abstractmethod
    async def obtener_duracion_promedio(
        self,
        *,
        categoria: Optional[str] = None,
        modelo: Optional[str] = None
    ) -> Optional[float]:
        """Calcula duración promedio en segundos."""
        raise NotImplementedError
    
    @abstractmethod
    async def obtener_usuarios_mas_activos(
        self,
        *,
        desde: Optional[datetime] = None,
        hasta: Optional[datetime] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Top N usuarios con más consultas."""
        raise NotImplementedError
    
    @abstractmethod
    async def buscar_por_contenido(
        self,
        termino: str,
        *,
        sede_id: Optional[int] = None,
        limit: int = 20
    ):
        """Búsqueda de texto en prompts."""
        raise NotImplementedError

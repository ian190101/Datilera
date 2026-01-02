# app/kernel/domain/exportacion/exportacion_entidad.py

from __future__ import annotations
from datetime import datetime, date, timedelta
from enum import Enum
from typing import Optional, Dict, Any, ClassVar
from pydantic import BaseModel, ConfigDict
from .errors import (
            ExportacionNoCompletadaError,
            ExportacionExpiradaError,
            ArchivoNoDisponibleError,
        )


class TipoReporte(str, Enum):
    """Tipos de reportes exportables del sistema."""
    # Académico
    ALUMNOS = "alumnos"
    GRUPOS = "grupos"
    ASISTENCIAS = "asistencias"
    REPORTES_DIARIOS = "reportes_diarios"
    ACTIVIDADES_PORTAFOLIO = "actividades_portafolio"
    CALIFICACIONES = "calificaciones"
    
    # Administrativo
    PERSONAL = "personal"
    HORARIOS = "horarios"
    PLANIFICACION = "planificacion"
    EVENTOS = "eventos"
    
    # Financiero
    PAGOS = "pagos"
    MENSUALIDADES = "mensualidades"
    COBRANZA = "cobranza"
    BALANCE = "balance"
    
    # Inventarios
    PRODUCTOS = "productos"
    MOVIMIENTOS_INVENTARIO = "movimientos_inventario"
    ALERTAS_STOCK = "alertas_stock"
    
    # Comunicaciones
    NOTIFICACIONES = "notificaciones"
    MENSAJES_CHAT = "mensajes_chat"
    COMUNICADOS = "comunicados"
    
    # Auditoría
    LOGS_SISTEMA = "logs_sistema"
    LOGS_MULTIMEDIA = "logs_multimedia"
    ACCIONES_USUARIOS = "acciones_usuarios"


class FormatoArchivo(str, Enum):
    """Formatos de archivo soportados."""
    PDF = "pdf"
    EXCEL = "excel"
    CSV = "csv"


class EstadoExportacion(str, Enum):
    """Estados del ciclo de vida de una exportación."""
    PENDIENTE = "pendiente"
    PROCESANDO = "procesando"
    COMPLETADO = "completado"
    ERROR = "error"


class Exportacion(BaseModel):
    """
    Entidad de dominio para exportaciones.
    Representa una solicitud de exportación de datos del sistema.
    """
    model_config = ConfigDict(from_attributes=True)
    
    # === CAMPOS DE INSTANCIA ===
    id: int
    usuario_id: int
    sede_id: int
    
    tipo_reporte: TipoReporte
    formato: FormatoArchivo
    
    filtros: Optional[Dict[str, Any]] = None
    plantilla_id: Optional[int] = None
    
    nombre_archivo: str
    url_descarga: Optional[str] = None
    ruta_archivo: Optional[str] = None
    tamano_bytes: Optional[int] = None
    
    estado: EstadoExportacion
    error_mensaje: Optional[str] = None
    
    solicitado_en: datetime
    procesado_en: Optional[datetime] = None
    fecha_expiracion: Optional[date] = None
    
    veces_descargado: int = 0
    ultima_descarga: Optional[datetime] = None
    
    # === CONSTANTES DE CLASE ===
    DIAS_EXPIRACION: ClassVar[int] = 3
    
    # === REGLAS DE NEGOCIO ===
    
    @property
    def esta_completada(self) -> bool:
        """Verifica si la exportación está completada."""
        return self.estado == EstadoExportacion.COMPLETADO
    
    @property
    def esta_pendiente(self) -> bool:
        """Verifica si la exportación está pendiente."""
        return self.estado == EstadoExportacion.PENDIENTE
    
    @property
    def tiene_error(self) -> bool:
        """Verifica si la exportación tiene error."""
        return self.estado == EstadoExportacion.ERROR
    
    @property
    def ha_expirado(self) -> bool:
        """Verifica si el archivo ha expirado."""
        if not self.fecha_expiracion:
            return False
        return date.today() > self.fecha_expiracion
    
    @property
    def puede_descargarse(self) -> bool:
        """Verifica si el archivo puede descargarse."""
        return (
            self.esta_completada
            and not self.ha_expirado
            and self.url_descarga is not None
            and self.ruta_archivo is not None
        )
    
    def calcular_fecha_expiracion(self) -> date:
        """Calcula la fecha de expiración desde la fecha de procesamiento."""
        if self.procesado_en:
            return self.procesado_en.date() + timedelta(days=self.DIAS_EXPIRACION)
        return date.today() + timedelta(days=self.DIAS_EXPIRACION)
    
    def validar_descarga(self) -> None:
        """
        Valida que la exportación pueda descargarse.
        Lanza excepciones específicas si no cumple condiciones.
        """
        
        
        if not self.esta_completada:
            raise ExportacionNoCompletadaError(self.id, self.estado)
        
        if self.ha_expirado:
            raise ExportacionExpiradaError(self.id, self.fecha_expiracion)
        
        if not self.ruta_archivo:
            raise ArchivoNoDisponibleError(self.id, "No se encontró la ruta del archivo")

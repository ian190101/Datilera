# app/infrastructure/db/models/exportacion/exportacion.py

from sqlalchemy import Column, Integer, String, DateTime, Date, Enum as SQLEnum, JSON, ForeignKey
from sqlalchemy.sql import func
from app.infrastructure.db.base import Base
import enum


class TipoReporte(str, enum.Enum):
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


class FormatoArchivo(str, enum.Enum):
    PDF = "pdf"
    EXCEL = "excel"
    CSV = "csv"


class EstadoExportacion(str, enum.Enum):
    PENDIENTE = "pendiente"
    PROCESANDO = "procesando"
    COMPLETADO = "completado"
    ERROR = "error"


class Exportacion(Base):
    """
    Tabla de auditoría de exportaciones del sistema.
    Rastrea todas las exportaciones generadas.
    """
    __tablename__ = "exportaciones"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Usuario que solicitó la exportación
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False, index=True)
    sede_id = Column(Integer, ForeignKey("sedes.id"), nullable=False, index=True)
    
    # Tipo y formato
    tipo_reporte = Column(SQLEnum(TipoReporte), nullable=False, index=True)
    formato = Column(SQLEnum(FormatoArchivo), nullable=False)
    
    # Filtros aplicados (almacenados como JSON)
    filtros = Column(JSON, nullable=True, comment="Filtros aplicados: fechas, IDs, columnas personalizadas")
    
    # Plantilla usada (si aplica)
    plantilla_id = Column(Integer, nullable=True, comment="ID de plantilla predefinida si se usó")
    
    # Información del archivo generado
    nombre_archivo = Column(String(255), nullable=False)
    url_descarga = Column(String(500), nullable=True)  # Null si aún no se generó
    ruta_archivo = Column(String(500), nullable=True, comment="Ruta en disco del archivo")
    tamano_bytes = Column(Integer, nullable=True)
    
    # Estado y fechas
    estado = Column(SQLEnum(EstadoExportacion), default=EstadoExportacion.PENDIENTE, nullable=False)
    error_mensaje = Column(String(500), nullable=True)
    
    solicitado_en = Column(DateTime, server_default=func.now(), nullable=False)
    procesado_en = Column(DateTime, nullable=True)
    fecha_expiracion = Column(Date, nullable=True, comment="Fecha en que se elimina automáticamente")
    
    # Estadísticas
    veces_descargado = Column(Integer, default=0)
    ultima_descarga = Column(DateTime, nullable=True)


class PlantillaExportacion(Base):
    """
    Plantillas predefinidas para exportaciones recurrentes.
    Ejemplo: "Reporte mensual de pagos", "Lista de alumnos activos".
    """
    __tablename__ = "plantillas_exportacion"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(150), nullable=False, unique=True)
    descripcion = Column(String(500), nullable=True)
    
    tipo_reporte = Column(SQLEnum(TipoReporte), nullable=False)
    formato_default = Column(SQLEnum(FormatoArchivo), nullable=False)
    
    # Configuración JSON
    columnas_incluidas = Column(JSON, nullable=False, comment="Lista de columnas a exportar")
    filtros_default = Column(JSON, nullable=True, comment="Filtros predefinidos")
    
    # Metadatos
    creado_por = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    creado_en = Column(DateTime, server_default=func.now())
    es_publica = Column(Integer, default=1, comment="1=visible para todos, 0=solo creador")
    activa = Column(Integer, default=1)

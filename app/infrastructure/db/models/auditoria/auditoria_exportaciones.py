# app/infrastructure/db/models/auditoria/auditoria_exportaciones.py

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Boolean, func, Index, Text
from app.infrastructure.db.base import Base
from sqlalchemy.orm import relationship


class AuditoriaExportacion(Base):
    """
    Registro de todas las exportaciones de datos (HU: auditar exportaciones).
    
    Crítico para:
    - Cumplimiento GDPR/privacidad
    - Detectar exportaciones masivas sospechosas
    - Saber qué datos se exportaron y cuándo
    """
    __tablename__ = "auditoria_exportaciones"

    id = Column(Integer, primary_key=True, autoincrement=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True, index=True)
    sede_id = Column(Integer, ForeignKey("sedes.id", ondelete="SET NULL"), nullable=True, index=True)
    
    # Tipo de exportación
    tipo = Column(String(50), nullable=False, index=True)
    # Valores: "pagos", "alumnos", "inventario", "reportes", "arqueo"
    
    # Formato
    formato = Column(String(20), nullable=False)
    # Valores: "excel", "pdf", "csv"
    
    # Filtros aplicados
    filtros = Column(JSON, nullable=True)
    # Ejemplo: {"fecha_desde": "2024-01-01", "sede_id": 1}
    
    # Cantidad de registros exportados
    total_registros = Column(Integer, nullable=False, default=0)
    
    # Columnas incluidas
    columnas = Column(JSON, nullable=True)
    
    # Ruta del archivo generado (temporal)
    ruta_archivo = Column(String(500), nullable=True)
    
    # Estado
    exitoso = Column(Boolean, nullable=False, default=True, index=True)
    mensaje_error = Column(Text, nullable=True)
    
    # Timestamps
    creado_en = Column(DateTime, nullable=False, server_default=func.now(), index=True)
    descargado_en = Column(DateTime, nullable=True)

    __table_args__ = (
        Index('idx_exportacion_usuario_fecha', 'usuario_id', 'creado_en'),
        Index('idx_exportacion_tipo_fecha', 'tipo', 'creado_en'),
    )

    usuario = relationship("Usuario", back_populates="auditoria_exportaciones")
    sede = relationship("Sede", back_populates="auditoria_exportaciones")
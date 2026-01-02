# app/infrastructure/db/models/calendario/evento_calendario.py

from sqlalchemy import Column, Integer, String, Date, DateTime, Text, Boolean, ForeignKey, Time, Index
from sqlalchemy.orm import relationship
from datetime import datetime

from app.infrastructure.db.base import Base


class EventoCalendario(Base):
    """Eventos del calendario (festividades, cumpleaños, etc.)."""
    
    __tablename__ = "eventos_calendario"
    
    # Identificación
    id = Column(Integer, primary_key=True, autoincrement=True)
    titulo = Column(String(150), nullable=False, index=True)
    descripcion = Column(Text, nullable=True)
    
    # Tipo
    tipo_evento_id = Column(Integer, ForeignKey("tipos_eventos.id"), nullable=False, index=True)
    
    # Fechas
    fecha = Column(Date, nullable=False, index=True)
    fecha_fin = Column(Date, nullable=True)
    todo_el_dia = Column(Boolean, default=True)
    hora_inicio = Column(Time, nullable=True)
    hora_fin = Column(Time, nullable=True)
    
    # Ubicación
    sede_id = Column(Integer, ForeignKey("sedes.id"), nullable=False, index=True)
    lugar = Column(String(100), nullable=True)
    
    # Relacionado
    relacionado_tipo = Column(String(50), nullable=True)
    relacionado_id = Column(Integer, nullable=True)
    
    # Aprobación
    aprobado = Column(Boolean, default=True)
    aprobado_por = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    aprobado_en = Column(DateTime, nullable=True)
    
    # Recordatorios
    recordatorio_dias_antes = Column(Integer, nullable=True)
    recordatorio_enviado = Column(Boolean, default=False)
    
    # Auditoría
    creado_por = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    creado_en = Column(DateTime, nullable=False, default=datetime.utcnow)
    actualizado_en = Column(DateTime, nullable=True, onupdate=datetime.utcnow)
    
    # Relaciones
    tipo_evento = relationship("TipoEvento", back_populates="eventos")
    sede = relationship("Sede", back_populates="eventos_calendario")
    creador = relationship("Usuario", foreign_keys=[creado_por])
    aprobador = relationship("Usuario", foreign_keys=[aprobado_por])
    planificaciones = relationship("PlanificacionActividad", back_populates="evento", cascade="all, delete-orphan")
    
    # Índices
    __table_args__ = (
        Index("idx_evento_fecha_sede", "fecha", "sede_id"),
        Index("idx_evento_tipo_fecha", "tipo_evento_id", "fecha"),
    )

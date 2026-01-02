# app/infrastructure/db/models/calendario/planificacion_actividad.py

from sqlalchemy import Column, Integer, String, Date, DateTime, Text, Boolean, ForeignKey, Time, Index
from sqlalchemy.orm import relationship
from datetime import datetime

from app.infrastructure.db.base import Base


class PlanificacionActividad(Base):
    """Planificación detallada de actividades."""
    
    __tablename__ = "planificaciones_actividades"
    
    # Identificación
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Evento asociado (opcional)
    evento_id = Column(Integer, ForeignKey("eventos_calendario.id", ondelete="CASCADE"), nullable=True, index=True)
    
    # Fecha y horarios
    fecha = Column(Date, nullable=False, index=True)
    hora_inicio = Column(Time, nullable=False)
    hora_fin = Column(Time, nullable=False)
    
    # Detalles
    titulo = Column(String(200), nullable=False)
    descripcion = Column(Text, nullable=True)
    objetivo = Column(Text, nullable=True)
    materiales = Column(Text, nullable=True)
    
    # Responsable
    profesora_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False, index=True)
    
    # Grupo
    paralelo_id = Column(Integer, ForeignKey("paralelos.id"), nullable=True, index=True)
    
    # Ubicación
    sede_id = Column(Integer, ForeignKey("sedes.id"), nullable=False, index=True)
    lugar = Column(String(100), nullable=True)
    
    # Estado
    completada = Column(Boolean, default=False)
    notas_ejecucion = Column(Text, nullable=True)
    
    # Auditoría
    creado_en = Column(DateTime, nullable=False, default=datetime.utcnow)
    actualizado_en = Column(DateTime, nullable=True, onupdate=datetime.utcnow)
    
    # Relaciones
    evento = relationship("EventoCalendario", back_populates="planificaciones")
    profesora = relationship("Usuario", foreign_keys=[profesora_id])
    paralelo = relationship("Paralelo", back_populates="planificaciones")
    sede = relationship("Sede", back_populates="planificaciones_actividades")
    
    # Índices
    __table_args__ = (
        Index("idx_planificacion_fecha_sede", "fecha", "sede_id"),
        Index("idx_planificacion_profesora_fecha", "profesora_id", "fecha"),
    )

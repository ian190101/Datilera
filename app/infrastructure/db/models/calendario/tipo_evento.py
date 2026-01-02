# app/infrastructure/db/models/calendario/tipo_evento.py

from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey, Index, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime

from app.infrastructure.db.base import Base


class TipoEvento(Base):
    """Tipos de eventos configurables (dinámicos por sede)."""
    
    __tablename__ = "tipos_eventos"
    
    # Identificación
    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(100), nullable=False, index=True)
    descripcion = Column(Text, nullable=True)
    
    # Estilo visual
    color = Column(String(7), nullable=False, default="#3B82F6")
    icono = Column(String(50), nullable=True)
    
    # Configuración
    requiere_aprobacion = Column(Boolean, default=False)
    visible_profesoras = Column(Boolean, default=True)
    visible_tutores = Column(Boolean, default=True)
    
    # Por sede
    sede_id = Column(Integer, ForeignKey("sedes.id"), nullable=False, index=True)
    
    # Estado
    activo = Column(Boolean, default=True, index=True)
    
    # Auditoría
    creado_por = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    creado_en = Column(DateTime, nullable=False, default=datetime.utcnow)
    actualizado_en = Column(DateTime, nullable=True, onupdate=datetime.utcnow)
    
    # Relaciones
    sede = relationship("Sede", back_populates="tipos_eventos")
    creador = relationship("Usuario", foreign_keys=[creado_por])
    eventos = relationship("EventoCalendario", back_populates="tipo_evento")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint("nombre", "sede_id", name="uq_tipo_evento_nombre_sede"),
    )

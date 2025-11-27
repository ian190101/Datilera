# app/infrastructure/db/models/alumnos/consentimientos.py

from sqlalchemy import Column, Integer, ForeignKey, Boolean, DateTime, Text
from sqlalchemy.orm import relationship
from app.infrastructure.db.base import Base
from datetime import datetime


class Consentimiento(Base):
    __tablename__ = "consentimientos"

    # ==================== CAMPOS EXISTENTES (OK, sin cambios) ====================
    id = Column(Integer, primary_key=True, index=True)
    alumno_id = Column(Integer, ForeignKey("alumnos.id"), nullable=False)
    autoriza_fotos = Column(Boolean, default=False)
    autoriza_videos = Column(Boolean, default=False)
    observaciones = Column(Text)
    creado_en = Column(DateTime, default=datetime.utcnow)
    actualizado_en = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # ==================== RELACIONES ====================
    alumno = relationship("Alumno", back_populates="consentimientos")

# app/infrastructure/db/models/alumnos/alumnos_paralelos.py

from sqlalchemy import Column, Integer, Date, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship
from app.infrastructure.db.base import Base
from datetime import datetime


class AlumnoParalelo(Base):
    __tablename__ = "alumnos_paralelos"

    # ==================== CAMPOS EXISTENTES (mantener) ====================
    id = Column(Integer, primary_key=True, index=True)
    alumno_id = Column(Integer, ForeignKey("alumnos.id"), nullable=False)
    paralelo_id = Column(Integer, ForeignKey("paralelos.id"), nullable=False)
    fecha_asignacion = Column(Date, nullable=False)
    activo = Column(Boolean, default=True)
    creado_en = Column(DateTime, default=datetime.utcnow)
    
    # ==================== RELACIONES ====================
    alumno = relationship("Alumno", back_populates="paralelos")
    paralelo = relationship("Paralelo", back_populates="alumnos_paralelos")

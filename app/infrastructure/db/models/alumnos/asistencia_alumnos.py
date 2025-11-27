# app/infrastructure/db/models/alumnos/asistencia_alumnos.py

from sqlalchemy import Column, Integer, String, Date, ForeignKey, Boolean, DateTime, Time  # NUEVO: Time
from sqlalchemy.orm import relationship
from app.infrastructure.db.base import Base
from datetime import datetime


class AsistenciaAlumno(Base):
    __tablename__ = "asistencia_alumnos"

    # ==================== CAMPOS EXISTENTES ====================
    id = Column(Integer, primary_key=True, index=True)
    alumno_id = Column(Integer, ForeignKey("alumnos.id"), nullable=False)
    fecha = Column(Date, nullable=False)
    estado = Column(String(20), nullable=False)  # presente, falta, retraso
    sede_id = Column(Integer, ForeignKey("sedes.id"), nullable=False)
    registrado_por_id = Column(Integer, ForeignKey("usuarios.id"))
    creado_en = Column(DateTime, default=datetime.utcnow)
    
    # ==================== CAMPOS NUEVOS ====================
    hora_retraso = Column(Time)  # NUEVO: hora a la que llegó si estado=retraso (HU: especificar hora de retraso con reloj estilo iPhone)
    observaciones = Column(String(500))  # NUEVO: comentarios adicionales opcionales
    
    # ==================== RELACIONES ====================
    alumno = relationship("Alumno", back_populates="asistencias")  # EXISTENTE
    sede = relationship("Sede")  # EXISTENTE
    registrado_por = relationship("Usuario")  # EXISTENTE (mantener)

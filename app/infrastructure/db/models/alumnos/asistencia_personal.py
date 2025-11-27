# app/infrastructure/db/models/alumnos/asistencia_personal.py

from sqlalchemy import Column, Integer, Date, Time, ForeignKey, String, DateTime
from sqlalchemy.orm import relationship
from app.infrastructure.db.base import Base
from datetime import datetime


class AsistenciaPersonal(Base):
    __tablename__ = "asistencia_personal"

    # ==================== CAMPOS EXISTENTES (OK, sin cambios) ====================
    id = Column(Integer, primary_key=True, index=True)
    personal_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    fecha = Column(Date, nullable=False)
    hora_entrada = Column(Time)
    hora_salida = Column(Time)
    sede_id = Column(Integer, ForeignKey("sedes.id"), nullable=False)
    registrado_por_id = Column(Integer, ForeignKey("usuarios.id"))
    creado_en = Column(DateTime, default=datetime.utcnow)
    
    # ==================== RELACIONES ====================
    personal = relationship("Usuario", foreign_keys=[personal_id])
    sede = relationship("Sede")
    registrado_por = relationship("Usuario", foreign_keys=[registrado_por_id])

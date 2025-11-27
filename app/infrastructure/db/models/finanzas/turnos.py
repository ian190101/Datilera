# app/infrastructure/db/models/finanzas/turnos.py

from sqlalchemy import Column, Integer, String, Time, Boolean, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from app.infrastructure.db.base import Base
from datetime import datetime

class Turno(Base):
    __tablename__ = "turnos"

    id = Column(Integer, primary_key=True, index=True)
    sede_id = Column(Integer, ForeignKey("sedes.id"), nullable=False)

    # Información del turno
    nombre = Column(String(80), nullable=False, unique=True, index=True)  # "Mañana", "Tarde", "Continuo", "Completo"
    descripcion = Column(String(200))
    hora_inicio = Column(Time, nullable=False)
    hora_fin = Column(Time, nullable=False)

    # Estado
    activo = Column(Boolean, default=True, server_default="1")

    # Auditoría
    creado_en = Column(DateTime, nullable=False, server_default=func.now())  # ← CORRECCIÓN AQUÍ
    actualizado_en = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    creado_por_id = Column(Integer, ForeignKey("usuarios.id"))

    # Relaciones
    sede = relationship("Sede", back_populates="turnos")
    alumnos = relationship("Alumno", back_populates="turno")
    precios = relationship("PrecioTurno", back_populates="turno")  # Relación con historial de precios
    creado_por = relationship("Usuario")

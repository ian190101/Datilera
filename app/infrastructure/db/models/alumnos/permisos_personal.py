# app/infrastructure/db/models/alumnos/permisos_personal.py

from sqlalchemy import Column, Integer, String, Date, ForeignKey, Text, Boolean, DateTime
from sqlalchemy.orm import relationship
from app.infrastructure.db.base import Base
from datetime import datetime


class PermisoPersonal(Base):
    __tablename__ = "permisos_personal"

    # ==================== CAMPOS EXISTENTES (OK, sin cambios) ====================
    id = Column(Integer, primary_key=True, index=True)
    personal_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    titulo = Column(String(150), nullable=False)
    descripcion = Column(Text)
    fecha_desde = Column(Date, nullable=False)
    fecha_hasta = Column(Date, nullable=False)
    respaldo_url = Column(String(500))  # imagen/PDF de respaldo (certificado médico, etc.)
    estado = Column(String(20), default="pendiente")  # pendiente, aprobado, rechazado
    sede_id = Column(Integer, ForeignKey("sedes.id"), nullable=False)
    aprobado_por_id = Column(Integer, ForeignKey("usuarios.id"))
    fecha_respuesta = Column(DateTime)
    creado_en = Column(DateTime, default=datetime.utcnow)
    
    # ==================== RELACIONES ====================
    personal = relationship("Usuario", foreign_keys=[personal_id])
    sede = relationship("Sede")
    aprobado_por = relationship("Usuario", foreign_keys=[aprobado_por_id])

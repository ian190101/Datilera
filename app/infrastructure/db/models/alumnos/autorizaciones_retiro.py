# app/infrastructure/db/models/alumnos/autorizaciones_retiro.py

from sqlalchemy import Column, Integer, ForeignKey, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from app.infrastructure.db.base import Base
from datetime import datetime


class AutorizacionRetiro(Base):
    __tablename__ = "autorizaciones_retiro"

    id = Column(Integer, primary_key=True, index=True)
    alumno_id = Column(Integer, ForeignKey("alumnos.id"), nullable=False)
    
    # Persona autorizada
    nombres_completos = Column(String(200), nullable=False)
    ci_numero = Column(String(20), nullable=False)
    ci_documento_url = Column(String(500))  # Foto del CI (obligatorio según HU)
    parentesco = Column(String(50))  # tio, abuelo, hermano, amigo familia, etc.
    celular = Column(String(15))
    
    # Estado
    activo = Column(Boolean, default=True)
    
    # Auditoría
    creado_en = Column(DateTime, default=datetime.utcnow)
    creado_por_id = Column(Integer, ForeignKey("usuarios.id"))
    
    # Relaciones
    alumno = relationship("Alumno", back_populates="autorizaciones_retiro")
    creado_por = relationship("Usuario")

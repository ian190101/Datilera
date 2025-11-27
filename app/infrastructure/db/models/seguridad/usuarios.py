# app/infrastructure/db/models/seguridad/usuarios.py

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, func
from sqlalchemy.orm import relationship  # ← AGREGAR si no está
from app.infrastructure.db.base import Base

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, autoincrement=True)
    sede_id = Column(Integer, ForeignKey("sedes.id", ondelete="RESTRICT"), nullable=False, index=True)
    username = Column(String(64), unique=True, nullable=False, index=True)
    hash_password = Column(String(255), nullable=False)
    nombres = Column(String(160), nullable=False)
    apellidos = Column(String(160), nullable=False)
    email = Column(String(120), nullable=True, index=True)
    telefono = Column(String(20), nullable=True)
    foto_perfil_url = Column(String(255), nullable=True)
    activo = Column(Boolean, nullable=False, default=True, server_default="1")
    creado_en = Column(DateTime, nullable=False, server_default=func.now())
    actualizado_en = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    
    ci_numero = Column(String(20))  # NUEVO
    direccion = Column(Text)  # NUEVO
    codigo_acceso = Column(String(6), unique=True, index=True)  # NUEVO
    codigo_usado = Column(Boolean, default=False)  # NUEVO
    codigo_expira_en = Column(DateTime)  # NUEVO
    
    # ==================== AGREGAR ESTA RELACIÓN ====================
    tutor = relationship("Tutor", back_populates="usuario", uselist=False)  # ← NUEVO: relación con tutores
    # ===============================================================

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, func
from app.infrastructure.db.base import Base

class Usuario(Base):
    __tablename__ = "usuarios"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    sede_id = Column(Integer, ForeignKey("sedes.id", ondelete="RESTRICT"), nullable=False, index=True)
    username = Column(String(64), unique=True, nullable=False, index=True)
    hash_password = Column(String(255), nullable=False)
    nombre_completo = Column(String(160), nullable=False)
    email = Column(String(120), nullable=True, index=True)
    telefono = Column(String(20), nullable=True)
    foto_perfil_url = Column(String(255), nullable=True)
    activo = Column(Boolean, nullable=False, default=True, server_default="1")
    creado_en = Column(DateTime, nullable=False, server_default=func.now())
    actualizado_en = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

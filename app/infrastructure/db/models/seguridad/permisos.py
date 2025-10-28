from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from app.infrastructure.db.base import Base

class Permiso(Base):
    __tablename__ = "permisos"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    vista = Column(String(80), nullable=False, index=True)
    accion = Column(String(30), nullable=False, index=True)
    descripcion = Column(String(200), nullable=True)
    activo = Column(Boolean, nullable=False, default=True, server_default="1")
    creado_en = Column(DateTime, nullable=False, server_default=func.now())

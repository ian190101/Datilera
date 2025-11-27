from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from app.infrastructure.db.base import Base

class Sede(Base):
    __tablename__ = "sedes"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    codigo = Column(String(10), unique=True, nullable=False, index=True)
    nombre = Column(String(120), nullable=False)
    direccion = Column(String(250), nullable=True)
    activo = Column(Boolean, nullable=False, default=True, server_default="1")
    creado_en = Column(DateTime, nullable=False, server_default=func.now())
    actualizado_en = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    config_alerta_vencimiento_dias = Column(String(15), nullable=True, server_default="5,3,1")
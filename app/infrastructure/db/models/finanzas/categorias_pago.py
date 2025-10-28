from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, func
from app.infrastructure.db.base import Base

class CategoriaPago(Base):
    __tablename__ = "categorias_pago"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(100), unique=True, nullable=False, index=True)
    descripcion = Column(Text, nullable=True)
    activo = Column(Boolean, nullable=False, default=True, server_default="1")
    creado_en = Column(DateTime, nullable=False, server_default=func.now())

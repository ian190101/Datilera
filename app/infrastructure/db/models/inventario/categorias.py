from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, func
from app.infrastructure.db.base import Base

class Categoria(Base):
    __tablename__ = "categorias"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    familia_id = Column(Integer, ForeignKey("familias.id", ondelete="RESTRICT"), nullable=False, index=True)
    nombre = Column(String(80), nullable=False, index=True)
    descripcion = Column(String(200), nullable=True)
    activo = Column(Boolean, nullable=False, default=True, server_default="1")
    creado_en = Column(DateTime, nullable=False, server_default=func.now())

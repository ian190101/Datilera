from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from app.infrastructure.db.base import Base
from sqlalchemy.orm import relationship

class Familia(Base):
    __tablename__ = "familias"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(80), unique=True, nullable=False, index=True)
    descripcion = Column(String(200), nullable=True)
    activo = Column(Boolean, nullable=False, default=True, server_default="1")
    creado_en = Column(DateTime, nullable=False, server_default=func.now())

    categorias = relationship("Categoria", back_populates="familia", cascade="all, delete-orphan")



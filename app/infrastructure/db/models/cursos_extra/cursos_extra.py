from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Numeric, func
from app.infrastructure.db.base import Base

class CursoExtra(Base):
    __tablename__ = "cursos_extra"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(120), nullable=False, index=True)
    descripcion = Column(Text, nullable=True)
    instructor = Column(String(120), nullable=False)
    sede_id = Column(Integer, ForeignKey("sedes.id", ondelete="RESTRICT"), nullable=False, index=True)
    activo = Column(Boolean, nullable=False, default=True, server_default="1")
    creado_en = Column(DateTime, nullable=False, server_default=func.now())
    actualizado_en = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    precio_interno = Column(Numeric(10,2), nullable=False, comment="Precio para alumnos regulares del jardín")
    precio_externo = Column(Numeric(10,2), nullable=False, comment="Precio para alumnos nuevos solo de curso extra")

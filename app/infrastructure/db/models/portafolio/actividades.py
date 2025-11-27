from sqlalchemy import Column, Integer, String, Text, Date, DateTime, ForeignKey, func
from app.infrastructure.db.base import Base

class Actividad(Base):
    __tablename__ = "actividades"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    alumno_id = Column(Integer, ForeignKey("alumnos.id", ondelete="RESTRICT"), nullable=True, index=True) 
    grupo_id = Column(Integer, ForeignKey("grupos.id", ondelete="SET NULL"), nullable=True,index=True)
    profesora_id = Column(Integer, ForeignKey("usuarios.id", ondelete="RESTRICT"), nullable=False, index=True)
    titulo = Column(String(150), nullable=False)
    descripcion = Column(Text, nullable=True)
    fecha_actividad = Column(Date, nullable=False, index=True)
    creado_en = Column(DateTime, nullable=False, server_default=func.now())
    actualizado_en = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

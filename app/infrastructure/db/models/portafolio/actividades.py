from sqlalchemy import Column, Integer, String, Text, Date, DateTime, ForeignKey, func, Enum as SQLEnum
from app.infrastructure.db.base import Base
from sqlalchemy.orm import relationship
import enum

# 1. Definimos los tipos de actividad basados en la imagen
class TipoActividad(str, enum.Enum):
    ALIMENTACION = "ALIMENTACION"
    HIGIENE = "HIGIENE"
    APRENDIZAJE = "APRENDIZAJE"
    FOTO = "FOTO"
    ANIMO = "ANIMO"
    SIESTA = "SIESTA"
    LOGROS = "LOGROS"
    OBSERVACION = "OBSERVACION"
    SALUD = "SALUD"
    VIDEO = "VIDEO"
    MEDICAMENTO = "MEDICAMENTO"
    ACCIDENTE = "ACCIDENTE"
    TAREA = "TAREA"

class Actividad(Base):
    __tablename__ = "actividades"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    alumno_id = Column(Integer, ForeignKey("alumnos.id", ondelete="RESTRICT"), nullable=True, index=True) 
    grupo_id = Column(Integer, ForeignKey("grupos.id", ondelete="SET NULL"), nullable=True,index=True)
    profesora_id = Column(Integer, ForeignKey("usuarios.id", ondelete="RESTRICT"), nullable=False, index=True)
    tipo = Column(SQLEnum(TipoActividad), nullable=False, default=TipoActividad.OBSERVACION)
    titulo = Column(String(150), nullable=False)
    descripcion = Column(Text, nullable=True)
    valor = Column(String(100), nullable=True) 
    hora = Column(String(10), nullable=True)
    fecha_actividad = Column(Date, nullable=False, index=True)
    creado_en = Column(DateTime, nullable=False, server_default=func.now())
    actualizado_en = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    alumno = relationship("Alumno", back_populates="actividades_portafolio")
    grupo = relationship("Grupo", back_populates="actividades")
    profesora = relationship("Usuario", back_populates="actividades_portafolio")
    media = relationship("ActividadMedia", back_populates="actividad", cascade="all, delete-orphan")

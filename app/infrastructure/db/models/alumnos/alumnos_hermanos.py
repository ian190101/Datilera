# app/infrastructure/db/models/alumnos/alumnos_hermanos.py

from sqlalchemy import Column, Integer, ForeignKey, String, DateTime
from sqlalchemy.orm import relationship
from app.infrastructure.db.base import Base
from datetime import datetime


class AlumnoHermano(Base):
    __tablename__ = "alumnos_hermanos"

    id = Column(Integer, primary_key=True, index=True)
    alumno_id = Column(Integer, ForeignKey("alumnos.id"), nullable=False)
    
    # Datos del hermano
    nombres_completos = Column(String(200), nullable=False)
    edad_anos = Column(Integer)
    lugar_ocupa = Column(Integer)  # 1=primero/mayor, 2=segundo, etc.
    
    # Si el hermano también está inscrito en el centro
    hermano_alumno_id = Column(Integer, ForeignKey("alumnos.id"))  # Referencia cruzada si está inscrito
    
    # Auditoría
    creado_en = Column(DateTime, default=datetime.utcnow)
    
    # Relaciones
    alumno = relationship("Alumno", foreign_keys=[alumno_id], back_populates="hermanos")
    hermano_inscrito = relationship("Alumno", foreign_keys=[hermano_alumno_id])

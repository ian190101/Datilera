# app/infrastructure/db/models/alumnos/alumnos_tutores.py

from sqlalchemy import Column, Integer, ForeignKey, Boolean, String, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from app.infrastructure.db.base import Base
from datetime import datetime


class AlumnoTutor(Base):
    __tablename__ = "alumnos_tutores"

    id = Column(Integer, primary_key=True, index=True)
    alumno_id = Column(Integer, ForeignKey("alumnos.id"), nullable=False)
    tutor_id = Column(Integer, ForeignKey("tutores.id"), nullable=False)
    
    # Tipo de relación específica
    tipo_relacion = Column(String(20), nullable=False)  # padre, madre, tutor_legal, abuelo, tio, otro
    es_principal = Column(Boolean, default=False)  # El tutor principal (aparece primero)
    tiene_custodia = Column(Boolean, default=True)  # Tiene custodia legal del menor
    recibe_notificaciones = Column(Boolean, default=True)  # Recibe notificaciones del sistema
    autorizado_retirar = Column(Boolean, default=True)  # Puede retirar al menor
    
    # Auditoría
    creado_en = Column(DateTime, default=datetime.utcnow)
    
    # Relaciones
    alumno = relationship("Alumno", back_populates="alumnos_tutores")
    tutor = relationship("Tutor", back_populates="alumnos_tutores")
    
    __table_args__ = (
        UniqueConstraint('alumno_id', 'tutor_id', name='uq_alumno_tutor'),
    )

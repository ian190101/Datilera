# app/infrastructure/db/models/alumnos/tutores.py

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Text, Date, DateTime
from sqlalchemy.orm import relationship
from app.infrastructure.db.base import Base
from datetime import datetime


class Tutor(Base):
    __tablename__ = "tutores"

    id = Column(Integer, primary_key=True, index=True)
    
    # Identificación
    ci_numero = Column(String(20), nullable=False, index=True)
    ci_complemento = Column(String(5))
    ci_expedido = Column(String(5))  # CBBA, LP, SC, etc.
    ci_documento_url = Column(String(500))  # Foto del CI
    
    # Datos personales
    nombres = Column(String(100), nullable=False)
    apellidos = Column(String(100), nullable=False)
    genero = Column(String(1))  # M/F
    fecha_nacimiento = Column(Date)
    foto_url = Column(String(500))
    
    # Contacto
    celular = Column(String(15), nullable=False, index=True)
    celular_alternativo = Column(String(15))
    email = Column(String(150))
    direccion = Column(Text)
    
    # Laboral
    profesion = Column(String(100))
    lugar_trabajo = Column(String(200))
    direccion_trabajo = Column(Text)
    telefono_trabajo = Column(String(15))
    
    # Cuenta en el sistema
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), unique=True)
    codigo_acceso = Column(String(6), unique=True, index=True)  # 6 caracteres para registrarse
    codigo_usado = Column(Boolean, default=False)
    codigo_expira_en = Column(DateTime)
    
    # Auditoría
    creado_en = Column(DateTime, default=datetime.utcnow)
    actualizado_en = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    usuario = relationship("Usuario", back_populates="tutor")
    alumnos = relationship("Alumno", secondary="alumnos_tutores", back_populates="tutores")
    alumnos_tutores = relationship("AlumnoTutor", back_populates="tutor")

from sqlalchemy import Column, Integer, String, Date, Boolean, DateTime, ForeignKey, Text, func
from app.infrastructure.db.base import Base

class Alumno(Base):
    __tablename__ = "alumnos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    sede_id = Column(Integer, ForeignKey("sedes.id", ondelete="RESTRICT"), nullable=False, index=True)
    tutor_id = Column(Integer, ForeignKey("tutores.id", ondelete="RESTRICT"), nullable=False, index=True)

    codigo = Column(String(30), unique=True, nullable=True, index=True)
    nombres = Column(String(120), nullable=False, index=True)
    apellidos = Column(String(120), nullable=False, index=True)
    documento = Column(String(30), nullable=True, index=True)
    fecha_nacimiento = Column(Date, nullable=False, index=True)

    direccion = Column(Text, nullable=True)
    telefono = Column(String(20), nullable=True)

    activo = Column(Boolean, nullable=False, default=True, server_default="1", index=True)
    creado_en = Column(DateTime, nullable=False, server_default=func.now())
    actualizado_en = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

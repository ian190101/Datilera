from sqlalchemy import Column, Integer, Text, Date, DateTime, ForeignKey, func, Boolean
from app.infrastructure.db.base import Base
from sqlalchemy.orm import relationship

class ReporteDiario(Base):
    __tablename__ = "reportes_diarios"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    profesora_id = Column(Integer, ForeignKey("usuarios.id", ondelete="RESTRICT"), nullable=False, index=True)
    fecha = Column(Date, nullable=False, index=True)
    contenido = Column(Text, nullable=False)
    creado_en = Column(DateTime, nullable=False, server_default=func.now())
    actualizado_en = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    alumno_id = Column(Integer, ForeignKey("alumnos.id", ondelete="RESTRICT"),nullable=False,index=True,)  
    enviado = Column(Boolean, nullable=False, server_default="0", index=True)
    enviado_en = Column(DateTime, nullable=True)
    confirmado = Column(Boolean, nullable=False, server_default="0", index=True)
    confirmado_en = Column(DateTime, nullable=True)

    profesora = relationship("Usuario", back_populates="reportes_diarios")
    alumno = relationship("Alumno", back_populates="reportes_diarios")
    lecturas_tutores = relationship("ReporteLecturaTutor", back_populates="reporte_diario", cascade="all, delete-orphan")
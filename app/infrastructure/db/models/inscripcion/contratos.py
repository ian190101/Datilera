from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, func
from app.infrastructure.db.base import Base

class Contrato(Base):
    __tablename__ = "contratos"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    formulario_id = Column(Integer, ForeignKey("formularios_inscripcion.id", ondelete="RESTRICT"), nullable=False, index=True)
    codigo_contrato = Column(String(30), unique=True, nullable=False, index=True)
    pdf_url = Column(String(255), nullable=True)
    fecha_emision = Column(Date, nullable=False, index=True)
    creado_en = Column(DateTime, nullable=False, server_default=func.now())

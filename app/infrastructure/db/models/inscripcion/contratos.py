from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, func, UniqueConstraint, JSON 
from app.infrastructure.db.base import Base

class Contrato(Base):
    __tablename__ = "contratos"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    formulario_id = Column(Integer, ForeignKey("formularios_inscripcion.id", ondelete="RESTRICT"), nullable=False, index=True)
    codigo_contrato = Column(String(30), unique=True, nullable=False, index=True)
    pdf_url = Column(String(255), nullable=True)
    fecha_emision = Column(Date, nullable=False, index=True)
    creado_en = Column(DateTime, nullable=False, server_default=func.now())
    sede_id = Column(Integer, ForeignKey("sedes.id", ondelete="RESTRICT"), nullable=False, index=True)  # <-- esto es nuevo
    plantilla_version = Column(Integer, nullable=True)  # <-- esto es nuevo
    variables_json = Column(JSON, nullable=True)  # <-- esto es nuevo
    numeracion_sede = Column(Integer, nullable=True, index=True)  # <-- esto es nuevo

    __table_args__ = (
        UniqueConstraint("sede_id", "numeracion_sede", name="uq_contrato_sede_num"),  # <-- esto es nuevo
    )
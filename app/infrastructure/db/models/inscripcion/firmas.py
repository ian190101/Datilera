from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from app.infrastructure.db.base import Base

class Firma(Base):
    __tablename__ = "firmas"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    formulario_id = Column(Integer, ForeignKey("formularios_inscripcion.id", ondelete="RESTRICT"), nullable=False, index=True)
    firmante = Column(String(120), nullable=False)
    firma_url = Column(String(255), nullable=False)
    firmado_en = Column(DateTime, nullable=False, server_default=func.now())

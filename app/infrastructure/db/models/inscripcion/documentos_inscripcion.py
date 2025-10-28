from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from app.infrastructure.db.base import Base

class DocumentoInscripcion(Base):
    __tablename__ = "documentos_inscripcion"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    formulario_id = Column(Integer, ForeignKey("formularios_inscripcion.id", ondelete="CASCADE"), nullable=False, index=True)
    tipo_documento = Column(String(80), nullable=False, index=True)
    url = Column(String(255), nullable=False)
    nombre_archivo = Column(String(120), nullable=False)
    creado_en = Column(DateTime, nullable=False, server_default=func.now())

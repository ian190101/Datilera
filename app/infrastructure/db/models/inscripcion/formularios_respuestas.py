from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, func
from app.infrastructure.db.base import Base

class FormularioRespuesta(Base):
    __tablename__ = "formularios_respuestas"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    formulario_id = Column(Integer, ForeignKey("formularios_inscripcion.id", ondelete="CASCADE"), nullable=False, index=True)
    campo = Column(String(80), nullable=False)
    valor = Column(Text, nullable=False)
    creado_en = Column(DateTime, nullable=False, server_default=func.now())

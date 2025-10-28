from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey, func
from app.infrastructure.db.base import Base

class IAConsulta(Base):
    __tablename__ = "ia_consultas"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="RESTRICT"), nullable=False, index=True)
    pregunta = Column(Text, nullable=False)
    respuesta = Column(Text, nullable=False)
    tokens_consumidos = Column(Integer, nullable=False, default=0)
    creado_en = Column(DateTime, nullable=False, server_default=func.now())

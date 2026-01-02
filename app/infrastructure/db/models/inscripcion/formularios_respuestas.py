from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, func, UniqueConstraint 
from app.infrastructure.db.base import Base
from sqlalchemy.orm import relationship

class FormularioRespuesta(Base):
    __tablename__ = "formularios_respuestas"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    formulario_id = Column(Integer, ForeignKey("formularios_inscripcion.id", ondelete="CASCADE"), nullable=False, index=True)
    campo = Column(String(80), nullable=False)
    valor = Column(Text, nullable=False)
    creado_en = Column(DateTime, nullable=False, server_default=func.now())
    seccion = Column(String(40), nullable=True, index=True)  # <-- esto es nuevo
    actualizado_en = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())  # <-- esto es nuevo

    __table_args__ = (
        UniqueConstraint("formulario_id", "campo", name="uq_form_campo"),  # <-- esto es nuevo
    )


    formulario = relationship("FormularioInscripcion", back_populates="respuestas")
from sqlalchemy import Column, Integer, Numeric, DateTime, ForeignKey, func
from app.infrastructure.db.base import Base

class CostoCursoExtra(Base):
    __tablename__ = "costos_curso_extra"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    curso_extra_id = Column(Integer, ForeignKey("cursos_extra.id", ondelete="CASCADE"), nullable=False, index=True)
    gestion = Column(Integer, nullable=False, index=True)
    monto = Column(Numeric(10, 2), nullable=False)
    creado_en = Column(DateTime, nullable=False, server_default=func.now())
    actualizado_en = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

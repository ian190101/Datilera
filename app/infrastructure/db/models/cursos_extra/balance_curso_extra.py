from sqlalchemy import Column, Integer, Numeric, Date, DateTime, ForeignKey, func, Enum as SQLEnum
from app.infrastructure.db.base import Base
import enum

class EstadoBalance(enum.Enum):
    pendiente = "pendiente"
    pagado = "pagado"

class BalanceCursoExtra(Base):
    __tablename__ = "balance_curso_extra"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    inscripcion_curso_extra_id = Column(Integer, ForeignKey("inscripciones_curso_extra.id", ondelete="RESTRICT"), nullable=False, index=True)
    monto_total = Column(Numeric(10, 2), nullable=False)
    monto_pagado = Column(Numeric(10, 2), nullable=False, default=0)
    saldo = Column(Numeric(10, 2), nullable=False)
    fecha_vencimiento = Column(Date, nullable=True, index=True)
    estado = Column(SQLEnum(EstadoBalance), nullable=False, default=EstadoBalance.pendiente, server_default="pendiente", index=True)
    creado_en = Column(DateTime, nullable=False, server_default=func.now())
    actualizado_en = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

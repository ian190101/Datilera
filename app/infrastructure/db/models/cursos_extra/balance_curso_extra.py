from sqlalchemy import Column, Integer, Numeric, Date, DateTime, ForeignKey, Enum as SQLEnum, func
from sqlalchemy.orm import relationship
from app.infrastructure.db.base import Base
import enum


class EstadoBalance(enum.Enum):
    """Estado del balance de pago del alumno inscrito"""
    PENDIENTE = "pendiente"
    PAGADO = "pagado"
    PARCIAL = "parcial"  # ← AGREGADO: para pagos parciales


class BalanceCursoExtra(Base):
    """
    Modelo para el balance/estado de cuenta individual de cada inscripción.
    Controla monto total, pagado y saldo pendiente.
    """
    __tablename__ = "balance_curso_extra"

    # ============ Campos Primarios ============
    id = Column(Integer, primary_key=True, autoincrement=True)
    inscripcion_curso_extra_id = Column(
        Integer, 
        ForeignKey("inscripciones_curso_extra.id", ondelete="RESTRICT"), 
        nullable=False, 
        index=True,
        unique=True  # ← AGREGADO: una inscripción tiene un solo balance
    )
    
    # ============ Montos ============
    monto_total = Column(Numeric(10, 2), nullable=False, comment="Monto total a pagar")
    monto_pagado = Column(Numeric(10, 2), nullable=False, default=0, comment="Monto ya pagado")
    saldo = Column(Numeric(10, 2), nullable=False, comment="Saldo pendiente (total - pagado)")
    
    # ============ Fechas y Estado ============
    fecha_vencimiento = Column(Date, nullable=True, index=True, comment="Fecha límite de pago (opcional)")
    estado = Column(
        SQLEnum(EstadoBalance), 
        nullable=False, 
        default=EstadoBalance.PENDIENTE,
        server_default="pendiente",
        index=True
    )
    
    # ============ Auditoría ============
    creado_en = Column(DateTime, nullable=False, server_default=func.now())
    actualizado_en = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    
    # ============ Relaciones ============
    inscripcion = relationship("InscripcionCursoExtra", back_populates="balance")
    pagos = relationship("PagoCursoExtra", back_populates="balance")

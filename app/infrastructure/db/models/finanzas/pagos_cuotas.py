"""Asignación auditable de cada pago a una cuota."""

from sqlalchemy import DECIMAL, Column, DateTime, ForeignKey, Index, Integer, UniqueConstraint, func
from sqlalchemy.orm import relationship

from app.infrastructure.db.base import Base


class PagoCuota(Base):
    """Conserva el historial completo de pagos totales y parciales de una cuota."""

    __tablename__ = "pagos_cuotas"

    id = Column(Integer, primary_key=True, autoincrement=True)
    pago_id = Column(Integer, ForeignKey("pagos.id", ondelete="RESTRICT"), nullable=False)
    cuota_id = Column(Integer, ForeignKey("cuotas_plan_pago.id", ondelete="RESTRICT"), nullable=False)
    monto_aplicado = Column(DECIMAL(10, 2), nullable=False)
    creado_en = Column(DateTime, nullable=False, server_default=func.now())

    pago = relationship("Pago", back_populates="asignaciones_cuotas")
    cuota = relationship("CuotaPlanPago", back_populates="asignaciones_pagos")

    __table_args__ = (
        UniqueConstraint("pago_id", "cuota_id", name="uq_pago_cuota"),
        Index("ix_pagos_cuotas_pago", "pago_id"),
        Index("ix_pagos_cuotas_cuota", "cuota_id"),
    )

# app/infrastructure/db/models/finanzas/cuota_plan_pago.py

from sqlalchemy import Column, Integer, Date, DateTime, String, ForeignKey, Index, DECIMAL
from sqlalchemy.orm import relationship
from datetime import datetime


from app.infrastructure.db.base import Base


class CuotaPlanPago(Base):
    """Cuotas individuales de un plan de pago (tabla de amortización)."""
    
    __tablename__ = "cuotas_plan_pago"
    
    # Identificación
    id = Column(Integer, primary_key=True, autoincrement=True)
    plan_id = Column(Integer, ForeignKey("planes_pago_personalizados.id", ondelete="CASCADE"), nullable=False, index=True)
    numero_cuota = Column(Integer, nullable=False)  # 1, 2, 3, ..., 12
    
    # Montos
    monto_cuota = Column(DECIMAL(10, 2), nullable=False)
    monto_pagado = Column(DECIMAL(10, 2), nullable=False, default=0.00)
    mora = Column(DECIMAL(10, 2), nullable=False, default=0.00)
    
    # Fechas
    fecha_vencimiento = Column(Date, nullable=False, index=True)
    fecha_pago = Column(DateTime, nullable=True)
    
    # Estado
    estado = Column(String(20), nullable=False, default='pendiente', index=True)
    # pendiente, pagada, vencida, cancelada
    
    # Relación con pago
    pago_id = Column(Integer, ForeignKey("pagos.id"), nullable=True)
    
    # Auditoría
    creado_en = Column(DateTime, nullable=False, default=datetime.utcnow)
    actualizado_en = Column(DateTime, nullable=True, onupdate=datetime.utcnow)
    
    # Relaciones
    plan = relationship("PlanPagoPersonalizado", back_populates="cuotas")
    pago = relationship("Pago", back_populates="cuotas")
    asignaciones_pagos = relationship("PagoCuota", back_populates="cuota")
    
    # Índices compuestos
    __table_args__ = (
        Index("idx_cuota_plan_numero", "plan_id", "numero_cuota"),
        Index("idx_cuota_plan_estado", "plan_id", "estado"),
        Index("idx_cuota_fecha_estado", "fecha_vencimiento", "estado"),
    )

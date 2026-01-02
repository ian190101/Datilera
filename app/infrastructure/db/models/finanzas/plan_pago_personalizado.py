# app/infrastructure/db/models/finanzas/plan_pago_personalizado.py

from sqlalchemy import Column, Integer, DECIMAL, Date, DateTime, Boolean, String, ForeignKey, Index
from sqlalchemy.orm import relationship
from datetime import datetime

from app.infrastructure.db.base import Base


class PlanPagoPersonalizado(Base):
    """Planes de pago personalizados de 3400 Bs con opcionales."""
    
    __tablename__ = "planes_pago_personalizados"
    
    # Identificación
    id = Column(Integer, primary_key=True, autoincrement=True)
    alumno_id = Column(Integer, ForeignKey("alumnos.id"), nullable=False, unique=True, index=True)
    
    # Montos base
    monto_base = Column(DECIMAL(10, 2), nullable=False, default=3400.00)
    
    # Material (opcional)
    incluye_material = Column(Boolean, nullable=False, default=False)
    monto_material = Column(DECIMAL(10, 2), nullable=False, default=0.00)
    
    # Merienda (opcional)
    incluye_merienda = Column(Boolean, nullable=False, default=False)
    monto_merienda = Column(DECIMAL(10, 2), nullable=False, default=0.00)
    
    # Total y cuotas
    monto_total = Column(DECIMAL(10, 2), nullable=False)  # Base + extras
    numero_cuotas = Column(Integer, nullable=False, default=12)
    monto_cuota = Column(DECIMAL(10, 2), nullable=False)  # Total / numero_cuotas
    
    # Vigencia
    fecha_inicio = Column(Date, nullable=False, index=True)
    fecha_fin = Column(Date, nullable=True)  # Se calcula automáticamente
    
    # Estado
    estado = Column(String(20), nullable=False, default='activo', index=True)
    # activo, completado, cancelado
    
    # Ubicación
    sede_id = Column(Integer, ForeignKey("sedes.id"), nullable=False, index=True)
    
    # Auditoría
    creado_por = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    creado_en = Column(DateTime, nullable=False, default=datetime.utcnow)
    actualizado_en = Column(DateTime, nullable=True, onupdate=datetime.utcnow)
    
    # Relaciones
    alumno = relationship("Alumno", back_populates="plan_pago")
    cuotas = relationship(
        "CuotaPlanPago", 
        back_populates="plan",
        cascade="all, delete-orphan",
        order_by="CuotaPlanPago.numero_cuota"
    )
    sede = relationship("Sede")
    creador = relationship("Usuario", foreign_keys=[creado_por])
    
    
    # Índices
    __table_args__ = (
        Index("idx_plan_alumno_estado", "alumno_id", "estado"),
        Index("idx_plan_sede_fecha", "sede_id", "fecha_inicio"),
    )

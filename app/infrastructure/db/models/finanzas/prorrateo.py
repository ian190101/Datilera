# app/infrastructure/db/models/finanzas/prorrateo.py

from sqlalchemy import Column, Integer, DECIMAL, Date, DateTime, Boolean, ForeignKey, Index
from sqlalchemy.orm import relationship
from datetime import datetime

from app.infrastructure.db.base import Base


class Prorrateo(Base):
    """Cálculos de prorrateo para primer mes de ingreso."""
    
    __tablename__ = "prorrateos"
    
    # Identificación
    id = Column(Integer, primary_key=True, autoincrement=True)
    alumno_id = Column(Integer, ForeignKey("alumnos.id"), nullable=False, index=True)
    
    # Fecha de ingreso
    fecha_ingreso = Column(Date, nullable=False, index=True)
    
    # Cálculo
    dias_cursados = Column(Integer, nullable=False)  # Del ingreso al fin de mes
    dias_mes = Column(Integer, nullable=False)  # Total de días del mes
    monto_completo = Column(DECIMAL(10, 2), nullable=False)  # Monto mensual normal
    monto_prorrateo = Column(DECIMAL(10, 2), nullable=False)  # (dias_cursados/dias_mes) * monto_completo
    
    # Estado
    aplicado = Column(Boolean, nullable=False, default=False, index=True)
    pago_id = Column(Integer, ForeignKey("pagos.id"), nullable=True)  # Referencia al pago generado
    
    # Ubicación
    sede_id = Column(Integer, ForeignKey("sedes.id"), nullable=False, index=True)
    
    # Auditoría
    creado_por = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    creado_en = Column(DateTime, nullable=False, default=datetime.utcnow)
    actualizado_en = Column(DateTime, nullable=True, onupdate=datetime.utcnow)
    
    # Relaciones
    alumno = relationship("Alumno", back_populates="prorrateos")
    pago = relationship("Pago")
    sede = relationship("Sede")
    creador = relationship("Usuario", foreign_keys=[creado_por])
    
    # Índices
    __table_args__ = (
        Index("idx_prorrateo_alumno_aplicado", "alumno_id", "aplicado"),
        Index("idx_prorrateo_sede_fecha", "sede_id", "fecha_ingreso"),
    )

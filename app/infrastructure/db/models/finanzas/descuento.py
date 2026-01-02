# app/infrastructure/db/models/finanzas/descuento.py

from sqlalchemy import Column, Integer, String, DECIMAL, Date, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from datetime import datetime

from app.infrastructure.db.base import Base


class Descuento(Base):
    """Descuentos aplicados (3% semestral, 6% anual)."""
    
    __tablename__ = "descuentos"
    
    # Identificación
    id = Column(Integer, primary_key=True, autoincrement=True)
    alumno_id = Column(Integer, ForeignKey("alumnos.id"), nullable=False, index=True)
    
    # Tipo y monto
    tipo = Column(String(20), nullable=False)  # 'semestral', 'anual'
    porcentaje = Column(DECIMAL(5, 2), nullable=False)  # 3.00 o 6.00
    monto_descuento = Column(DECIMAL(10, 2), nullable=False)
    
    # Período de vigencia
    periodo_inicio = Column(Date, nullable=False)
    periodo_fin = Column(Date, nullable=False)
    
    # Estado
    estado = Column(String(20), nullable=False, default='activo', index=True)  
    # activo, vencido, cancelado
    
    # Ubicación
    sede_id = Column(Integer, ForeignKey("sedes.id"), nullable=False, index=True)
    
    # Auditoría
    aplicado_por = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    aplicado_en = Column(DateTime, nullable=False, default=datetime.utcnow)
    creado_en = Column(DateTime, nullable=False, default=datetime.utcnow)
    actualizado_en = Column(DateTime, nullable=True, onupdate=datetime.utcnow)
    
    # Relaciones
    alumno = relationship("Alumno", back_populates="descuentos")
    sede = relationship("Sede")
    aplicador = relationship("Usuario", foreign_keys=[aplicado_por])
    
    # Índices compuestos
    __table_args__ = (
        Index("idx_descuento_alumno_estado", "alumno_id", "estado"),
        Index("idx_descuento_periodo", "periodo_inicio", "periodo_fin"),
        Index("idx_descuento_sede_tipo", "sede_id", "tipo"),
    )

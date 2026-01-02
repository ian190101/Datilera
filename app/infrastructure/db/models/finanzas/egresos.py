# app/infrastructure/db/models/finanzas/egresos.py
from sqlalchemy import Column, Integer, String, Numeric, Date, DateTime, ForeignKey, Text, func, Boolean
from app.infrastructure.db.base import Base
from sqlalchemy.orm import relationship

class Egreso(Base):
    __tablename__ = "egresos"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    sede_id = Column(Integer, ForeignKey("sedes.id", ondelete="RESTRICT"), nullable=False, index=True)
    categoria_egreso_id = Column(Integer, ForeignKey("categorias_egreso.id", ondelete="RESTRICT"), nullable=False, index=True)
    
    monto = Column(Numeric(10, 2), nullable=False)
    fecha_egreso = Column(Date, nullable=False, index=True)
    
    concepto = Column(String(200), nullable=True)  # Descripción del gasto
    numero_comprobante = Column(String(80), nullable=True, index=True)
    metodo_pago = Column(String(50), nullable=True)  # efectivo, transferencia, etc.
    
    proveedor = Column(String(200), nullable=True)  # A quién se pagó
    observaciones = Column(Text, nullable=True)
    
    registrado_por = Column(Integer, ForeignKey("usuarios.id", ondelete="RESTRICT"), nullable=False, index=True)
    
    # Estado para anulaciones
    anulado = Column(Boolean, nullable=False, default=False, server_default="0")
    anulado_por = Column(Integer, ForeignKey("usuarios.id", ondelete="RESTRICT"), nullable=True)
    anulado_en = Column(DateTime, nullable=True)
    motivo_anulacion = Column(Text, nullable=True)
    
    creado_en = Column(DateTime, nullable=False, server_default=func.now())
    
    # Relaciones
    sede = relationship("Sede", back_populates="egresos")
    #categoria = relationship("CategoriaEgreso", back_populates="egresos")
    usuario_registro = relationship("Usuario", foreign_keys=[registrado_por], back_populates="egresos_registrados")
    usuario_anulacion = relationship("Usuario", foreign_keys=[anulado_por], back_populates="egresos_anulados")
    libro_caja_item = relationship("LibroCaja", back_populates="egreso", uselist=False, cascade="all, delete-orphan")
    
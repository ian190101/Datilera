from sqlalchemy import Column, Integer, String, Text, Numeric, Date, DateTime, ForeignKey, Boolean, func
from app.infrastructure.db.base import Base

class Conciliacion(Base):
    __tablename__ = "conciliaciones"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    pago_id = Column(Integer, ForeignKey("pagos.id", ondelete="RESTRICT"), nullable=False, index=True)
    comprobante_id = Column(Integer, ForeignKey("comprobantes.id", ondelete="RESTRICT"), nullable=True, index=True)
    monto_conciliado = Column(Numeric(10, 2), nullable=False)
    fecha_conciliacion = Column(Date, nullable=False, index=True)
    conciliado = Column(Boolean, nullable=False, default=False, server_default="0", index=True)
    observaciones = Column(Text, nullable=True)
    conciliado_por = Column(Integer, ForeignKey("usuarios.id", ondelete="RESTRICT"), nullable=False, index=True)
    creado_en = Column(DateTime, nullable=False, server_default=func.now())

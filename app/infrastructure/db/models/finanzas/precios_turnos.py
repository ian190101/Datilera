from sqlalchemy import Column, Integer, Numeric, DateTime, ForeignKey, func, UniqueConstraint
from app.infrastructure.db.base import Base

class PrecioTurno(Base):
    __tablename__ = "precios_turnos"
    __table_args__ = (
        UniqueConstraint("turno_id", "categoria_pago_id", "gestion", name="uq_turno_categoria_gestion"),
    )
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    turno_id = Column(Integer, ForeignKey("turnos.id", ondelete="RESTRICT"), nullable=False, index=True)
    categoria_pago_id = Column(Integer, ForeignKey("categorias_pago.id", ondelete="RESTRICT"), nullable=False, index=True)
    gestion = Column(Integer, nullable=False, index=True)
    monto = Column(Numeric(10, 2), nullable=False)
    creado_en = Column(DateTime, nullable=False, server_default=func.now())
    actualizado_en = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

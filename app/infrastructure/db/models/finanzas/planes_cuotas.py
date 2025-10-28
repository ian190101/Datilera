from sqlalchemy import Column, Integer, Numeric, Date, DateTime, ForeignKey, func, Enum as SQLEnum
from app.infrastructure.db.base import Base
import enum

class EstadoCuota(enum.Enum):
    pendiente = "pendiente"
    pagado = "pagado"
    vencido = "vencido"

class PlanCuota(Base):
    __tablename__ = "planes_cuotas"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    plan_pago_id = Column(Integer, ForeignKey("planes_pago.id", ondelete="CASCADE"), nullable=False, index=True)
    numero_cuota = Column(Integer, nullable=False)
    monto = Column(Numeric(10, 2), nullable=False)
    fecha_vencimiento = Column(Date, nullable=False, index=True)
    estado = Column(SQLEnum(EstadoCuota), nullable=False, default=EstadoCuota.pendiente, server_default="pendiente", index=True)
    creado_en = Column(DateTime, nullable=False, server_default=func.now())
    actualizado_en = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, func
from app.infrastructure.db.base import Base
from sqlalchemy.orm import relationship

class PlanPago(Base):
    __tablename__ = "planes_pago"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    alumno_id = Column(Integer, ForeignKey("alumnos.id", ondelete="RESTRICT"), nullable=False, index=True)
    gestion = Column(Integer, nullable=False, index=True)
    monto_total = Column(Numeric(10, 2), nullable=False)
    descripcion = Column(String(200), nullable=True)
    creado_en = Column(DateTime, nullable=False, server_default=func.now())
    actualizado_en = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())


    alumno = relationship("Alumno", back_populates="planes_pago")
    #cuotas = relationship("CuotaPlanPago", back_populates="plan_simple", cascade="all, delete-orphan")

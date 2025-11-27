from sqlalchemy import Column, Integer, Numeric, Date, DateTime, String, Text, ForeignKey, func
from sqlalchemy.orm import relationship
from app.infrastructure.db.base import Base


class IngresoCursoExtra(Base):
    """
    Modelo para consolidar ingresos totales de un curso extra (suma de pagos).
    Facilita el cálculo de balance: ganancia = ingresos - gastos.
    Se actualiza automáticamente con cada pago registrado.
    """
    __tablename__ = "ingresos_curso_extra"

    # ============ Campos Primarios ============
    id = Column(Integer, primary_key=True, autoincrement=True)
    curso_extra_id = Column(
        Integer, 
        ForeignKey("cursos_extra.id", ondelete="CASCADE"), 
        nullable=False, 
        index=True
    )
    
    # ============ Montos ============
    total_ingresos = Column(Numeric(10, 2), nullable=False, default=0, comment="Suma total de pagos recibidos")
    total_gastos = Column(Numeric(10, 2), nullable=False, default=0, comment="Suma total de costos/gastos")
    ganancia_bruta = Column(Numeric(10, 2), nullable=False, default=0, comment="ingresos - gastos")
    
    # ============ Distribución de Ganancias ============
    ganancia_institucion = Column(
        Numeric(10, 2), 
        nullable=False, 
        default=0, 
        comment="Ganancia para la institución según porcentaje"
    )
    ganancia_instructor = Column(
        Numeric(10, 2), 
        nullable=False, 
        default=0, 
        comment="Ganancia para el instructor según porcentaje"
    )
    
    # ============ Auditoría ============
    actualizado_en = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    
    # ============ Relaciones ============
    curso = relationship("CursoExtra")

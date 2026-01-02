#app/infraestructura/db/modelos/portafolio/reporte_lecturas_tutores.py
from sqlalchemy import Column, Integer, DateTime, ForeignKey, func, UniqueConstraint, Boolean
from app.infrastructure.db.base import Base
from sqlalchemy.orm import relationship


class ReporteLecturaTutor(Base):
    __tablename__ = "reporte_lecturas_tutores"
    __table_args__ = (
        UniqueConstraint("reporte_diario_id", "tutor_id", name="uq_reporte_tutor"),
    )
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    reporte_diario_id = Column(Integer, ForeignKey("reportes_diarios.id", ondelete="CASCADE"), nullable=False, index=True)
    tutor_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False, index=True)
    leido_en = Column(DateTime, nullable=False, server_default=func.now())
    leido = Column(Boolean, nullable=False, server_default="1",)  


    reporte_diario = relationship("ReporteDiario", back_populates="lecturas_tutores")
    tutor = relationship("Usuario", back_populates="lecturas_reportes_diarios")
from sqlalchemy import Column, Integer, Date, DateTime, ForeignKey, UniqueConstraint, func
from app.infrastructure.db.base import Base

class HorarioParalelo(Base):
    __tablename__ = "horarios_paralelos"
    __table_args__ = (
        UniqueConstraint("paralelo_id", "horario_id", "desde", name="uq_paralelo_horario_desde"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    paralelo_id = Column(Integer, ForeignKey("paralelos.id", ondelete="RESTRICT"), nullable=False, index=True)
    horario_id = Column(Integer, ForeignKey("horarios.id", ondelete="RESTRICT"), nullable=False, index=True)
    desde = Column(Date, nullable=False, index=True)
    hasta = Column(Date, nullable=True, index=True)
    creado_en = Column(DateTime, nullable=False, server_default=func.now())

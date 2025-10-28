from sqlalchemy import Column, Integer, Date, DateTime, ForeignKey, UniqueConstraint, func
from app.infrastructure.db.base import Base

class ParaleloProfesora(Base):
    __tablename__ = "paralelos_profesoras"
    __table_args__ = (
        UniqueConstraint("paralelo_id", "profesora_id", "gestion", name="uq_paralelo_profesora_gestion"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    paralelo_id = Column(Integer, ForeignKey("paralelos.id", ondelete="RESTRICT"), nullable=False, index=True)
    profesora_id = Column(Integer, ForeignKey("usuarios.id", ondelete="RESTRICT"), nullable=False, index=True)  # usuario con rol Profesora
    gestion = Column(Integer, nullable=False, index=True)
    desde = Column(Date, nullable=True, index=True)
    hasta = Column(Date, nullable=True, index=True)
    creado_en = Column(DateTime, nullable=False, server_default=func.now())

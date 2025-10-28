from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, UniqueConstraint, func
from app.infrastructure.db.base import Base

class Paralelo(Base):
    __tablename__ = "paralelos"
    __table_args__ = (
        UniqueConstraint("grupo_id", "letra", name="uq_grupo_letra"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    grupo_id = Column(Integer, ForeignKey("grupos.id", ondelete="RESTRICT"), nullable=False, index=True)
    letra = Column(String(5), nullable=False, index=True)  # p.ej. "A", "B"
    capacidad = Column(Integer, nullable=True)
    activo = Column(Boolean, nullable=False, default=True, server_default="1", index=True)
    creado_en = Column(DateTime, nullable=False, server_default=func.now())

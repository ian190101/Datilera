from sqlalchemy import Column, Integer, String, Time, DateTime, func
from app.infrastructure.db.base import Base

class Horario(Base):
    __tablename__ = "horarios"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(80), nullable=False, index=True)  # p.ej. "Mañana", "Tarde"
    hora_inicio = Column(Time, nullable=False)
    hora_fin = Column(Time, nullable=False)
    creado_en = Column(DateTime, nullable=False, server_default=func.now())

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func, Text, UniqueConstraint
from app.infrastructure.db.base import Base
from sqlalchemy import Enum as SQLEnum
import enum

class TipoFirmante(enum.Enum):  # <-- esto es nuevo
    madre = "madre"  # <-- esto es nuevo
    padre = "padre"  # <-- esto es nuevo
    tutor = "tutor"  # <-- esto es nuevo

class Firma(Base):
    __tablename__ = "firmas"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    formulario_id = Column(Integer, ForeignKey("formularios_inscripcion.id", ondelete="RESTRICT"), nullable=False, index=True)
    firmante = Column(String(120), nullable=False)
    firma_url = Column(String(255), nullable=False)
    firmado_en = Column(DateTime, nullable=False, server_default=func.now())
    tipo_firmante = Column(SQLEnum(TipoFirmante), nullable=False, index=True)  # <-- esto es nuevo
    ip = Column(String(50), nullable=True)  # <-- esto es nuevo
    user_agent = Column(Text, nullable=True)  # <-- esto es nuevo

    __table_args__ = (
        UniqueConstraint("formulario_id", "tipo_firmante", name="uq_firma_form_tipo"),  # <-- esto es nuevo
    )
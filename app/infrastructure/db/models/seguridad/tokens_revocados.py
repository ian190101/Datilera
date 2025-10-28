from sqlalchemy import Column, Integer, String, DateTime, func
from app.infrastructure.db.base import Base

class TokenRevocado(Base):
    __tablename__ = "tokens_revocados"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    jti = Column(String(100), unique=True, nullable=False, index=True)
    tipo = Column(String(20), nullable=False, index=True)
    revocado_en = Column(DateTime, nullable=False, server_default=func.now())

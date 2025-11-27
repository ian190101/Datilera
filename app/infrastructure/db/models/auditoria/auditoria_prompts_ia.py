# app/infrastructure/db/models/auditoria/auditoria_prompts_ia.py

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Boolean, func, Index
from app.infrastructure.db.base import Base


class AuditoriaPromptIA(Base):
    """
    Registro de consultas a IA (HU: registrar auditoría de prompts/respuestas).
    
    Necesario para:
    - Auditar uso de IA
    - Controlar costos (tokens)
    - Detectar consultas sensibles
    - Cumplimiento de privacidad
    """
    __tablename__ = "auditoria_prompts_ia"

    id = Column(Integer, primary_key=True, autoincrement=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True, index=True)
    sede_id = Column(Integer, ForeignKey("sedes.id", ondelete="SET NULL"), nullable=True, index=True)
    
    # Datos del prompt
    prompt_original = Column(Text, nullable=False)
    prompt_sanitizado = Column(Text, nullable=True)  # Con datos sensibles enmascarados
    
    # Respuesta
    respuesta = Column(Text, nullable=True)
    
    # Tokens consumidos
    tokens_prompt = Column(Integer, nullable=True)
    tokens_respuesta = Column(Integer, nullable=True)
    tokens_total = Column(Integer, nullable=True)
    
    # Modelo utilizado
    modelo = Column(String(50), nullable=True)
    # Ejemplo: "gpt-4", "deepseek-chat"
    
    # Costo estimado (en USD)
    costo_usd = Column(String(20), nullable=True)
    
    # Categoría de consulta
    categoria = Column(String(50), nullable=True, index=True)
    # Valores: "reporte", "busqueda", "estadistica", "ayuda"
    
    # Contiene datos sensibles (post-análisis)
    tiene_datos_sensibles = Column(Boolean, nullable=False, default=False, index=True)
    
    # Estado
    exitoso = Column(Boolean, nullable=False, default=True, index=True)
    mensaje_error = Column(Text, nullable=True)
    
    # Duración (segundos)
    duracion_segundos = Column(Integer, nullable=True)
    
    # Timestamps
    creado_en = Column(DateTime, nullable=False, server_default=func.now(), index=True)

    __table_args__ = (
        Index('idx_prompt_usuario_fecha', 'usuario_id', 'creado_en'),
        Index('idx_prompt_categoria_fecha', 'categoria', 'creado_en'),
    )

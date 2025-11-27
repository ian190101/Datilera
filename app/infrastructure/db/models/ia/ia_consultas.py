# app/infrastructure/db/models/ia/ia_consultas.py

"""
Modelo SQLAlchemy: IAConsulta (mejorado)
Tabla: ia_consultas
"""
from __future__ import annotations
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON, Numeric
from sqlalchemy.orm import declarative_base
from app.infrastructure.db.base import Base


class IAConsulta(Base):
    """
    Modelo de base de datos para consultas a IA.
    
    Almacena:
    - Prompt y respuesta
    - Proveedor utilizado (OpenAI, Perplexity, etc.)
    - Modelo específico (gpt-4, claude-3, etc.)
    - Tokens y costos
    - Metadata y contexto
    """
    __tablename__ = "ia_consultas"
    
    # PK
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Usuario y Sede (si aplica)
    usuario_id = Column(Integer, nullable=True, index=True)
    sede_id = Column(Integer, nullable=True, index=True)
    
    # Proveedor y Modelo
    proveedor = Column(String(50), nullable=False, index=True)  # openai, perplexity, gemini, grok
    modelo = Column(String(100), nullable=False)  # gpt-4-turbo, claude-3-opus, etc.
    
    # Consulta
    prompt = Column(Text, nullable=False)
    prompt_sanitizado = Column(Text, nullable=True)  # Opcional: con datos sensibles removidos
    respuesta = Column(Text, nullable=True)
    
    # Tokens y Costos
    tokens_prompt = Column(Integer, nullable=True)
    tokens_respuesta = Column(Integer, nullable=True)
    tokens_total = Column(Integer, nullable=True)
    costo_usd = Column(Numeric(10, 6), nullable=True)  # Decimal para precisión
    
    # Metadata
    categoria = Column(String(50), nullable=True, index=True)  # consulta, reporte, analisis, etc.
    contexto = Column(JSON, nullable=True)  # Contexto adicional (filtros, parámetros, etc.)
    
    # Estado
    exitoso = Column(Boolean, default=True, nullable=False)
    mensaje_error = Column(Text, nullable=True)
    duracion_segundos = Column(Integer, nullable=True)
    
    # Seguridad
    tiene_datos_sensibles = Column(Boolean, default=False, nullable=False)
    
    # Timestamps
    creado_en = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    def __repr__(self) -> str:
        return f"<IAConsulta(id={self.id}, proveedor={self.proveedor}, modelo={self.modelo})>"
    

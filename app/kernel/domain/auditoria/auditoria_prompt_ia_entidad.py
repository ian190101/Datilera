# app/kernel/domain/auditoria/auditoria_prompt_ia_entidad.py

"""
Entidad de Dominio: AuditoriaPromptIA
Representa una consulta a IA.
"""
from __future__ import annotations
from datetime import datetime
from typing import Optional
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field, field_validator


class AuditoriaPromptIA(BaseModel):
    """
    Entidad de dominio para auditoría de consultas a IA.
    """
    id: int = 0
    usuario_id: Optional[int] = None
    sede_id: Optional[int] = None
    
    # Datos del prompt
    prompt_original: str = Field(..., min_length=1)
    prompt_sanitizado: Optional[str] = None
    
    # Respuesta
    respuesta: Optional[str] = None
    
    # Tokens consumidos
    tokens_prompt: Optional[int] = Field(None, ge=0)
    tokens_respuesta: Optional[int] = Field(None, ge=0)
    tokens_total: Optional[int] = Field(None, ge=0)
    
    # Modelo utilizado
    modelo: Optional[str] = Field(None, max_length=50)
    
    # Costo estimado (en USD)
    costo_usd: Optional[Decimal] = Field(None, ge=0)
    
    # Categoría
    categoria: Optional[str] = Field(None, max_length=50)
    
    # Datos sensibles
    tiene_datos_sensibles: bool = False
    
    # Estado
    exitoso: bool = True
    mensaje_error: Optional[str] = None
    
    # Duración
    duracion_segundos: Optional[int] = Field(None, ge=0)
    
    # Timestamps
    creado_en: datetime = Field(default_factory=datetime.utcnow)
    
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        from_attributes=True,
        frozen=False,
    )
    
    @field_validator("categoria")
    @classmethod
    def validar_categoria(cls, v: Optional[str]) -> Optional[str]:
        """Valida que la categoría sea válida."""
        if v is None:
            return v
        categorias_validas = {
            "reporte", "busqueda", "estadistica", "ayuda",
            "analisis", "prediccion", "consulta"
        }
        if v.lower() not in categorias_validas:
            raise ValueError(f"Categoría debe ser una de: {categorias_validas}")
        return v.lower()
    
    @field_validator("modelo")
    @classmethod
    def validar_modelo(cls, v: Optional[str]) -> Optional[str]:
        """Valida que el modelo sea reconocido."""
        if v is None:
            return v
        modelos_conocidos = {
            "gpt-4", "gpt-4-turbo", "gpt-3.5-turbo",
            "deepseek-chat", "deepseek-coder",
            "claude-3", "gemini-pro"
        }
        # Advertencia si el modelo no es conocido (pero no falla)
        if v.lower() not in modelos_conocidos:
            pass  # Permitir modelos nuevos
        return v
    
    def calcular_costo_aproximado(self) -> Optional[Decimal]:
        """Calcula costo aproximado basado en tokens (precios de OpenAI GPT-4)."""
        if self.tokens_total is None:
            return None
        
        # Precio aproximado por 1000 tokens (USD)
        precio_por_1k = Decimal("0.03")  # Promedio GPT-4
        
        costo = (Decimal(self.tokens_total) / Decimal("1000")) * precio_por_1k
        return round(costo, 6)
    
    def es_costoso(self, umbral_tokens: int = 10000) -> bool:
        """Verifica si la consulta consumió muchos tokens."""
        if self.tokens_total is None:
            return False
        return self.tokens_total >= umbral_tokens

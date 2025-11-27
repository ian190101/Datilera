# app/kernel/domain/ia/ia_consulta_entidad.py

"""
Entidad de Dominio: IAConsulta
Representa una consulta a un proveedor de IA.
"""
from __future__ import annotations
from datetime import datetime
from typing import Optional, Dict, Any
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field, field_validator


class IAConsulta(BaseModel):
    """
    Entidad de dominio para consultas a IA.
    
    Representa una interacción con cualquier proveedor de IA
    (OpenAI, Perplexity, Gemini, Grok, etc.)
    """
    id: int = 0
    usuario_id: Optional[int] = None
    sede_id: Optional[int] = None
    
    # Proveedor y Modelo
    proveedor: str = Field(..., min_length=1, max_length=50)
    modelo: str = Field(..., min_length=1, max_length=100)
    
    # Consulta y Respuesta
    prompt: str = Field(..., min_length=1)
    prompt_sanitizado: Optional[str] = None
    respuesta: Optional[str] = None
    
    # Tokens y Costos
    tokens_prompt: Optional[int] = Field(None, ge=0)
    tokens_respuesta: Optional[int] = Field(None, ge=0)
    tokens_total: Optional[int] = Field(None, ge=0)
    costo_usd: Optional[Decimal] = Field(None, ge=0)
    
    # Metadata
    categoria: Optional[str] = Field(None, max_length=50)
    contexto: Optional[Dict[str, Any]] = None
    
    # Estado
    exitoso: bool = True
    mensaje_error: Optional[str] = None
    duracion_segundos: Optional[int] = Field(None, ge=0)
    
    # Seguridad
    tiene_datos_sensibles: bool = False
    
    # Timestamps
    creado_en: datetime = Field(default_factory=datetime.utcnow)
    
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        from_attributes=True,
        frozen=False,
    )
    
    @field_validator("proveedor")
    @classmethod
    def validar_proveedor(cls, v: str) -> str:
        """Valida que el proveedor sea reconocido."""
        proveedores_validos = {
            "openai", "perplexity", "anthropic", "google", 
            "gemini", "grok", "deepseek", "mistral"
        }
        if v.lower() not in proveedores_validos:
            # Permitir proveedores nuevos pero advertir
            pass
        return v.lower()
    
    @field_validator("categoria")
    @classmethod
    def validar_categoria(cls, v: Optional[str]) -> Optional[str]:
        """Valida que la categoría sea válida."""
        if v is None:
            return v
        categorias_validas = {
            "consulta", "reporte", "analisis", "busqueda",
            "estadistica", "ayuda", "prediccion"
        }
        if v.lower() not in categorias_validas:
            raise ValueError(f"Categoría debe ser una de: {categorias_validas}")
        return v.lower()
    
    def calcular_costo_aproximado(self) -> Optional[Decimal]:
        """Calcula costo aproximado si no está disponible."""
        if self.costo_usd:
            return self.costo_usd
        
        if self.tokens_total is None:
            return None
        
        # Precios aproximados por 1K tokens (USD)
        precios = {
            "openai": {"gpt-4": 0.03, "gpt-3.5-turbo": 0.002},
            "anthropic": {"claude-3": 0.03},
            "google": {"gemini-pro": 0.0005},
        }
        
        # Buscar precio
        proveedor_precios = precios.get(self.proveedor, {})
        precio_por_1k = Decimal(str(proveedor_precios.get(self.modelo.split("-")[0], 0.02)))
        
        return (Decimal(str(self.tokens_total)) / Decimal("1000")) * precio_por_1k
    
    def es_costoso(self, umbral_tokens: int = 10000) -> bool:
        """Verifica si la consulta consumió muchos tokens."""
        if self.tokens_total is None:
            return False
        return self.tokens_total >= umbral_tokens
    
    def tiene_error(self) -> bool:
        """Verifica si la consulta tuvo error."""
        return not self.exitoso or self.mensaje_error is not None

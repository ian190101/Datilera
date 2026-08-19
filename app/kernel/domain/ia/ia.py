from abc import ABC, abstractmethod
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union

# --- DTOs (Data Transfer Objects) para estandarizar entrada/salida ---

class IAMessage(BaseModel):
    role: str  # 'user', 'assistant', 'system'
    content: str

class IARequest(BaseModel):
    prompt: str
    messages: List[IAMessage] = Field(default_factory=list)  # Historial de chat
    system_instruction: Optional[str] = None  # Instrucción "MCP" (rol del sistema)
    contexto: Optional[Dict[str, Any]] = None  # Datos extra (JSON) para RAG o contexto
    temperature: float = 0.7
    max_tokens: int = 2048

class IAResponse(BaseModel):
    content: str
    raw_response: Optional[Any] = None  # Respuesta cruda del proveedor (debug)
    model_name: str
    
    # Métricas para costos
    tokens_prompt: int = 0
    tokens_response: int = 0
    tokens_total: int = 0
    cost_usd: float = 0.0
    successful: bool = True
    error_message: Optional[str] = None

# --- PUERTO (Interfaz) ---

class IAProviderPort(ABC):
    """
    Contrato que deben cumplir todos los proveedores de IA (Gemini, OpenAI, etc).
    """
    
    @abstractmethod
    def get_nombre_proveedor(self) -> str:
        """Retorna el nombre clave del proveedor (ej: 'gemini', 'openai')"""
        pass

    @abstractmethod
    async def generar_respuesta(self, request: IARequest) -> IAResponse:
        """Procesa el prompt y retorna una respuesta estandarizada"""
        pass

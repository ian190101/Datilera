# app/kernel/application/auditoria/auditoria_prompts_ia/registrar_prompt_ia.py

"""
Caso de Uso: Registrar Prompt IA
"""
from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, Field

from app.kernel.domain.auditoria import AuditoriaPromptIA
from app.infrastructure.db.repositories.auditoria import AuditoriaPromptsIARepository


# ===== DTO =====

class RegistrarPromptIADTO(BaseModel):
    """DTO para registrar un prompt de IA."""
    usuario_id: Optional[int] = Field(None, gt=0)
    sede_id: Optional[int] = Field(None, gt=0)
    prompt_original: str = Field(..., min_length=1)
    prompt_sanitizado: Optional[str] = None
    respuesta: Optional[str] = None
    tokens_prompt: Optional[int] = Field(None, ge=0)
    tokens_respuesta: Optional[int] = Field(None, ge=0)
    tokens_total: Optional[int] = Field(None, ge=0)
    modelo: Optional[str] = Field(None, max_length=50)
    costo_usd: Optional[str] = None
    categoria: Optional[str] = Field(None, max_length=50)
    tiene_datos_sensibles: bool = False
    exitoso: bool = True
    mensaje_error: Optional[str] = None
    duracion_segundos: Optional[int] = Field(None, ge=0)


# ===== Caso de Uso =====

class RegistrarPromptIACU:
    """
    Caso de Uso: Registrar Prompt IA.
    
    Responsabilidad: Registrar consultas a IA (ChatGPT).
    Según HU: Integración con ChatGPT para consultas sobre BD.
    Necesario auditar uso de IA, control de costos y detectar consultas sensibles.
    """
    
    def __init__(self, repo: AuditoriaPromptsIARepository):
        self.repo = repo
    
    async def ejecutar(self, dto: RegistrarPromptIADTO) -> AuditoriaPromptIA:
        """
        Registra una consulta a IA.
        
        Args:
            dto: Datos del prompt
            
        Returns:
            Entidad de dominio AuditoriaPromptIA
        """
        # Registrar en infraestructura
        model = await self.repo.registrar(
            usuario_id=dto.usuario_id,
            sede_id=dto.sede_id,
            prompt_original=dto.prompt_original,
            prompt_sanitizado=dto.prompt_sanitizado,
            respuesta=dto.respuesta,
            tokens_prompt=dto.tokens_prompt,
            tokens_respuesta=dto.tokens_respuesta,
            tokens_total=dto.tokens_total,
            modelo=dto.modelo,
            costo_usd=dto.costo_usd,
            categoria=dto.categoria,
            tiene_datos_sensibles=dto.tiene_datos_sensibles,
            exitoso=dto.exitoso,
            mensaje_error=dto.mensaje_error,
            duracion_segundos=dto.duracion_segundos,
        )
        
        # Mapear a entidad de dominio
        return AuditoriaPromptIA.model_validate(model)

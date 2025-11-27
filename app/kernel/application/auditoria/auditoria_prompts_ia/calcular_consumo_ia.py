# app/kernel/application/auditoria/auditoria_prompts_ia/calcular_consumo_ia.py

"""
Caso de Uso: Calcular Consumo de IA
"""
from __future__ import annotations
from datetime import datetime
from typing import Optional, Dict
from pydantic import BaseModel, Field

from app.infrastructure.db.repositories.auditoria import AuditoriaPromptsIARepository


# ===== DTOs =====

class CalcularTokensConsumidosDTO(BaseModel):
    """DTO para calcular tokens consumidos."""
    usuario_id: Optional[int] = Field(None, gt=0)
    sede_id: Optional[int] = Field(None, gt=0)
    desde: Optional[datetime] = None
    hasta: Optional[datetime] = None


class CalcularCostoTotalDTO(BaseModel):
    """DTO para calcular costo total."""
    usuario_id: Optional[int] = Field(None, gt=0)
    sede_id: Optional[int] = Field(None, gt=0)
    desde: Optional[datetime] = None
    hasta: Optional[datetime] = None


# ===== Caso de Uso =====

class CalcularConsumoIACU:
    """
    Caso de Uso: Calcular Consumo de IA.
    
    Responsabilidad: Calcular tokens y costos de uso de IA.
    Según HU: Control de costos de ChatGPT.
    Crítico para gestión de presupuesto de IA.
    """
    
    def __init__(self, repo: AuditoriaPromptsIARepository):
        self.repo = repo
    
    async def tokens_consumidos(self, dto: CalcularTokensConsumidosDTO) -> Dict[str, int]:
        """
        Calcula total de tokens consumidos.
        
        Args:
            dto: Filtros de cálculo
            
        Returns:
            Dict con tokens_prompt, tokens_respuesta y tokens_total
        """
        return await self.repo.calcular_tokens_consumidos(
            usuario_id=dto.usuario_id,
            sede_id=dto.sede_id,
            desde=dto.desde,
            hasta=dto.hasta
        )
    
    async def costo_total(self, dto: CalcularCostoTotalDTO) -> float:
        """
        Calcula costo total en USD.
        
        Args:
            dto: Filtros de cálculo
            
        Returns:
            Costo total en USD
        """
        return await self.repo.calcular_costo_total(
            usuario_id=dto.usuario_id,
            sede_id=dto.sede_id,
            desde=dto.desde,
            hasta=dto.hasta
        )

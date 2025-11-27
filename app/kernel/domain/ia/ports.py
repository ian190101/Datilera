# app/kernel/domain/ia/ports.py

"""
Puertos (Interfaces) del Dominio de IA.

Define los contratos que debe cumplir la infraestructura.
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional, Dict, Any


class IAConsultasRepositoryPort(ABC):
    """
    Puerto para repositorio de consultas a IA.
    
    Trabaja con datos primitivos y modelos SQLAlchemy.
    El mapeo a entidades se hace en la capa de aplicación.
    """
    
    @abstractmethod
    async def registrar(
        self,
        usuario_id: Optional[int],
        sede_id: Optional[int],
        proveedor: str,
        modelo: str,
        prompt: str,
        *,
        prompt_sanitizado: Optional[str] = None,
        respuesta: Optional[str] = None,
        tokens_prompt: Optional[int] = None,
        tokens_respuesta: Optional[int] = None,
        tokens_total: Optional[int] = None,
        costo_usd: Optional[str] = None,
        categoria: Optional[str] = None,
        contexto: Optional[Dict[str, Any]] = None,
        exitoso: bool = True,
        mensaje_error: Optional[str] = None,
        duracion_segundos: Optional[int] = None,
        tiene_datos_sensibles: bool = False,
    ):
        """Registra una consulta a IA."""
        raise NotImplementedError
    
    @abstractmethod
    async def obtener_por_id(self, consulta_id: int):
        """Obtiene una consulta por ID."""
        raise NotImplementedError
    
    @abstractmethod
    async def listar_por_usuario(
        self,
        usuario_id: int,
        *,
        proveedor: Optional[str] = None,
        desde: Optional[datetime] = None,
        hasta: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0
    ):
        """Lista consultas de un usuario."""
        raise NotImplementedError
    
    @abstractmethod
    async def listar_por_proveedor(
        self,
        proveedor: str,
        *,
        desde: Optional[datetime] = None,
        hasta: Optional[datetime] = None,
        limit: int = 100
    ):
        """Lista consultas por proveedor."""
        raise NotImplementedError
    
    @abstractmethod
    async def calcular_consumo(
        self,
        *,
        usuario_id: Optional[int] = None,
        proveedor: Optional[str] = None,
        desde: Optional[datetime] = None,
        hasta: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Calcula consumo de tokens y costos."""
        raise NotImplementedError


class IAProviderPort(ABC):
    """
    Puerto para proveedores de IA (MCP - Model Context Protocol).
    
    Define la interfaz estándar que debe implementar cada proveedor.
    """
    
    @abstractmethod
    async def consultar(
        self,
        prompt: str,
        *,
        modelo: Optional[str] = None,
        temperatura: float = 0.7,
        max_tokens: Optional[int] = None,
        contexto: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Realiza una consulta al proveedor de IA.
        
        Args:
            prompt: Texto de la consulta
            modelo: Modelo específico a usar (opcional)
            temperatura: Creatividad de la respuesta (0-1)
            max_tokens: Límite de tokens de respuesta
            contexto: Contexto adicional para la consulta
            
        Returns:
            Dict con:
                - respuesta: str
                - tokens_prompt: int
                - tokens_respuesta: int
                - tokens_total: int
                - modelo_usado: str
                - costo_usd: float (opcional)
        """
        raise NotImplementedError
    
    @abstractmethod
    def get_nombre_proveedor(self) -> str:
        """Retorna el nombre del proveedor."""
        raise NotImplementedError
    
    @abstractmethod
    def get_modelos_disponibles(self) -> list[str]:
        """Retorna lista de modelos disponibles."""
        raise NotImplementedError
    
    @abstractmethod
    async def validar_conexion(self) -> bool:
        """Valida que el proveedor esté disponible."""
        raise NotImplementedError

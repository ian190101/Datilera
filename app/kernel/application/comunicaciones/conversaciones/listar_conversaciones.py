# app/kernel/application/comunicaciones/conversaciones/listar_conversaciones.py

from typing import List
from app.kernel.domain.comunicaciones import (
    Conversacion,
    ConversacionRepositoryPort,
)


class ListarConversacionesUseCase:
    """Caso de uso: Listar conversaciones del usuario (US-COM-007).
    
    Reglas:
    - Ordenadas por ultima_actividad_en DESC
    - Filtros opcionales: sede, cerradas
    - Paginación
    """

    def __init__(self, conversacion_repo: ConversacionRepositoryPort):
        self.conversacion_repo = conversacion_repo

    async def ejecutar(
        self,
        usuario_id: int,
        sede_id: int | None = None,
        cerradas: bool | None = None,
        limite: int = 20,
        offset: int = 0,
    ) -> List[Conversacion]:
        """Lista conversaciones del usuario.
        
        Args:
            usuario_id: Usuario que solicita
            sede_id: Filtrar por sede (opcional)
            cerradas: Filtrar por estado (opcional)
            limite: Máximo resultados
            offset: Saltar registros
            
        Returns:
            Lista de conversaciones
        """
        return await self.conversacion_repo.listar_por_usuario(
            usuario_id=usuario_id,
            sede_id=sede_id,
            cerradas=cerradas,
            limite=limite,
            offset=offset,
        )

# app/kernel/application/comunicaciones/conversaciones/crear_conversacion.py

from typing import List
from app.kernel.domain.comunicaciones import (
    Conversacion,
    Participante,
    ConversacionRepositoryPort,
    ParticipanteRepositoryPort,
    ParticipantesInsuficientes,
)


class CrearConversacionUseCase:
    """Caso de uso: Crear una conversación (US-COM-001).
    
    Reglas:
    - Asunto obligatorio (≤120 chars)
    - Mínimo 2 participantes
    - Estado inicial: ABIERTA
    - Por sede
    """

    def __init__(
        self,
        conversacion_repo: ConversacionRepositoryPort,
        participante_repo: ParticipanteRepositoryPort,
    ):
        self.conversacion_repo = conversacion_repo
        self.participante_repo = participante_repo

    async def ejecutar(
        self,
        sede_id: int,
        asunto: str,
        creado_por_id: int,
        participantes: List[Participante],
        titulo: str | None = None,
        descripcion: str | None = None,
    ) -> Conversacion:
        """Crea una conversación con participantes.
        
        Args:
            sede_id: ID de la sede
            asunto: Asunto de la conversación (obligatorio)
            creado_por_id: Usuario que crea la conversación
            participantes: Lista de participantes (≥2)
            titulo: Título opcional
            descripcion: Descripción opcional
            
        Returns:
            Conversación creada
            
        Raises:
            ParticipantesInsuficientes: Si hay menos de 2 participantes
            AsuntoInvalido: Si el asunto está vacío o excede límite
        """
        # Validar participantes
        if not participantes or len(participantes) < 2:
            raise ParticipantesInsuficientes(len(participantes) if participantes else 0)

        # Crear conversación (validaciones en entidad)
        conversacion = await self.conversacion_repo.crear(
            sede_id=sede_id,
            asunto=asunto,
            creado_por_id=creado_por_id,
            participantes=participantes,
            titulo=titulo,
            descripcion=descripcion,
        )

        # Agregar participantes a la tabla many-to-many
        for participante in participantes:
            await self.participante_repo.agregar(
                conversacion_id=conversacion.id,
                participante=participante,
            )

        return conversacion

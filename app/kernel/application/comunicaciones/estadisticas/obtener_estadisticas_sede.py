# app/kernel/application/comunicaciones/estadisticas/obtener_estadisticas_sede.py

from typing import Dict, List
from app.kernel.domain.comunicaciones import (
    ConversacionRepositoryPort,
    MensajeRepositoryPort,
)


class ObtenerEstadisticasSedeUseCase:
    """Caso de uso: Obtener estadísticas de comunicaciones por sede.
    
    Útil para reportes administrativos y dashboards.
    """

    def __init__(
        self,
        conversacion_repo: ConversacionRepositoryPort,
        mensaje_repo: MensajeRepositoryPort,
    ):
        self.conversacion_repo = conversacion_repo
        self.mensaje_repo = mensaje_repo

    async def ejecutar(
        self,
        sede_id: int,
        usuarios_ids: List[int],
    ) -> Dict[str, any]:
        """Obtiene estadísticas de comunicaciones de una sede.
        
        Args:
            sede_id: ID de la sede
            usuarios_ids: Lista de IDs de usuarios de la sede
            
        Returns:
            Diccionario con estadísticas agregadas:
            {
                'conversaciones': {
                    'total': int,
                    'abiertas': int,
                    'cerradas': int,
                    'por_usuario': {usuario_id: count, ...}
                },
                'mensajes': {
                    'total': int,
                    'por_usuario': {usuario_id: {'enviados': int, 'recibidos': int}, ...}
                }
            }
        """
        # Estadísticas de conversaciones
        total_conversaciones_abiertas = 0
        total_conversaciones_cerradas = 0
        conversaciones_por_usuario = {}

        for usuario_id in usuarios_ids:
            abiertas = await self.conversacion_repo.contar_por_usuario(
                usuario_id=usuario_id,
                sede_id=sede_id,
                cerradas=False,
            )
            cerradas = await self.conversacion_repo.contar_por_usuario(
                usuario_id=usuario_id,
                sede_id=sede_id,
                cerradas=True,
            )
            
            total_conversaciones_abiertas += abiertas
            total_conversaciones_cerradas += cerradas
            conversaciones_por_usuario[usuario_id] = abiertas + cerradas

        # Estadísticas de mensajes
        total_mensajes = 0
        mensajes_por_usuario = {}

        for usuario_id in usuarios_ids:
            stats = await self.mensaje_repo.contar_enviados_recibidos(
                usuario_id=usuario_id
            )
            mensajes_por_usuario[usuario_id] = stats
            total_mensajes += stats['enviados'] + stats['recibidos']

        return {
            'sede_id': sede_id,
            'conversaciones': {
                'total': total_conversaciones_abiertas + total_conversaciones_cerradas,
                'abiertas': total_conversaciones_abiertas,
                'cerradas': total_conversaciones_cerradas,
                'por_usuario': conversaciones_por_usuario,
            },
            'mensajes': {
                'total': total_mensajes,
                'por_usuario': mensajes_por_usuario,
            },
        }

# app/kernel/application/comunicaciones/estadisticas/obtener_estadisticas_usuario.py

from typing import Dict
from app.kernel.domain.comunicaciones import (
    ConversacionRepositoryPort,
    MensajeRepositoryPort,
    NotificacionRepositoryPort,
)


class ObtenerEstadisticasUsuarioUseCase:
    """Caso de uso: Obtener estadísticas de comunicaciones del usuario.
    
    Incluye:
    - Total de conversaciones (abiertas/cerradas)
    - Total de mensajes (enviados/recibidos)
    - Total de notificaciones (leídas/no leídas)
    - Agrupación de notificaciones por tipo
    """

    def __init__(
        self,
        conversacion_repo: ConversacionRepositoryPort,
        mensaje_repo: MensajeRepositoryPort,
        notificacion_repo: NotificacionRepositoryPort,
    ):
        self.conversacion_repo = conversacion_repo
        self.mensaje_repo = mensaje_repo
        self.notificacion_repo = notificacion_repo

    async def ejecutar(self, usuario_id: int) -> Dict[str, any]:
        """Obtiene estadísticas de comunicaciones del usuario.
        
        Args:
            usuario_id: Usuario a consultar
            
        Returns:
            Diccionario con estadísticas:
            {
                'conversaciones': {
                    'total': int,
                    'abiertas': int,
                    'cerradas': int
                },
                'mensajes': {
                    'enviados': int,
                    'recibidos': int,
                    'total': int
                },
                'notificaciones': {
                    'total': int,
                    'no_leidas': int,
                    'por_tipo': {'tipo1': count, 'tipo2': count, ...}
                }
            }
        """
        # Conversaciones
        total_conversaciones = await self.conversacion_repo.contar_por_usuario(
            usuario_id=usuario_id
        )
        conversaciones_abiertas = await self.conversacion_repo.contar_por_usuario(
            usuario_id=usuario_id,
            cerradas=False,
        )
        conversaciones_cerradas = await self.conversacion_repo.contar_por_usuario(
            usuario_id=usuario_id,
            cerradas=True,
        )

        # Mensajes
        mensajes_stats = await self.mensaje_repo.contar_enviados_recibidos(
            usuario_id=usuario_id
        )

        # Notificaciones
        notificaciones_no_leidas = await self.notificacion_repo.contar_no_leidas(
            usuario_id=usuario_id
        )
        notificaciones_por_tipo = await self.notificacion_repo.contar_por_tipo(
            usuario_id=usuario_id
        )
        total_notificaciones = sum(notificaciones_por_tipo.values())

        return {
            'conversaciones': {
                'total': total_conversaciones,
                'abiertas': conversaciones_abiertas,
                'cerradas': conversaciones_cerradas,
            },
            'mensajes': {
                'enviados': mensajes_stats['enviados'],
                'recibidos': mensajes_stats['recibidos'],
                'total': mensajes_stats['enviados'] + mensajes_stats['recibidos'],
            },
            'notificaciones': {
                'total': total_notificaciones,
                'no_leidas': notificaciones_no_leidas,
                'por_tipo': notificaciones_por_tipo,
            },
        }

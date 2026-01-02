# app/kernel/application/comunicaciones/notificaciones/agrupar_por_tipo.py

from collections import defaultdict
from typing import Dict

# Importamos la entidad real (¡esto es lo que faltaba!)
from app.kernel.domain.comunicaciones.notificacion_entidad import Notificacion

# Puerto del repositorio
from app.kernel.domain.comunicaciones import NotificacionRepositoryPort


class AgruparNotificacionesPorTipoUseCase:
    """Caso de uso: Agrupar notificaciones por tipo (US-COM-008).
    
    Reglas:
    - Retorna diccionario tipo → lista de notificaciones
    - Solo del usuario autenticado
    - Ordenadas por reciente (asumimos que el repo ya las devuelve así)
    - Incluye contador por tipo + total general
    """

    def __init__(self, notificacion_repo: NotificacionRepositoryPort):
        self.notificacion_repo = notificacion_repo

    async def ejecutar(self, usuario_id: int) -> Dict[str, dict]:
        """Agrupa todas las notificaciones del usuario por tipo.

        Returns:
            {
                "notificaciones": {
                    "pago_vencimiento": [Notificacion, ...],
                    "nuevo_mensaje": [Notificacion, ...],
                    ...
                },
                "estadisticas": {
                    "pago_vencimiento": 5,
                    "nuevo_mensaje": 3,
                    "total": 8
                }
            }
        """
        # 1. Obtener todas las notificaciones del usuario
        notificaciones = await self.notificacion_repo.listar_por_usuario(
            usuario_id=usuario_id,
            leidas=None,    # Traer leídas y no leídas
            limite=1000,    # Suficiente para la gran mayoría de usuarios
            offset=0,
        )

        # 2. Agrupación con tipos explícitos → ¡ADIÓS Any!
        agrupadas: Dict[str, list[Notificacion]] = defaultdict(list)
        estadisticas: Dict[str, int] = defaultdict(int)

        for notif in notificaciones:
            # notif.tipo es str gracias a tu field_validator
            agrupadas[notif.tipo].append(notif)   # ← ¡Ahora .append está perfectamente tipado!
            estadisticas[notif.tipo] += 1

        # Total general
        estadisticas["total"] = len(notificaciones)

        # Convertimos defaultdict → dict normal para la respuesta (más limpio y serializable)
        return {
            "notificaciones": dict(agrupadas),
            "estadisticas": dict(estadisticas),
        }
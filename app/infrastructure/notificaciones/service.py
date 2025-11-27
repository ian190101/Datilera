# app/infrastructure/notificaciones/service.py
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

# 1. Importamos la Interfaz y el DTO nuevos
from app.kernel.domain.notificaciones.notificaciones import (
    AbstractNotificacionesService, 
    CrearNotificacionInput
)

class NotificacionesService(AbstractNotificacionesService):
    """
    Implementación concreta del servicio de notificaciones.
    Por ahora es un MOCK (simulación) para que funcione el Portafolio.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def notificar_nuevo_reporte(self, reporte_id: int, tutor_ids: List[int]) -> None:
        # Método antiguo (puedes mantenerlo o redirigirlo al nuevo)
        print(f"--- [MOCK] Notificando Reporte #{reporte_id} a {tutor_ids} ---")

    # 2. IMPLEMENTAMOS EL NUEVO MÉTODO OBLIGATORIO
    async def enviar_notificacion(self, input_data: CrearNotificacionInput) -> None:
        """
        Simula el envío de una notificación genérica (Push/Email).
        """
        print(f"--- [MOCK NOTIFICACIÓN] ---")
        print(f"PARA: Usuario ID {input_data.usuario_id}")
        print(f"TÍTULO: {input_data.titulo}")
        print(f"MENSAJE: {input_data.mensaje}")
        print(f"DATA: {input_data.data}")
        print(f"---------------------------")
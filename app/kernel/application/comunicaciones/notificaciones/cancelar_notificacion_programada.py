# app/kernel/application/comunicaciones/notificaciones/cancelar_notificacion_programada.py

from app.kernel.domain.comunicaciones import (
    NotificacionRepositoryPort,
    NotificacionNoEncontrada,
    NotificacionYaEnviada,
)


class CancelarNotificacionProgramadaUseCase:
    """Caso de uso: Cancelar notificación programada.
    
    Reglas:
    - Solo se pueden cancelar notificaciones no enviadas
    - Marca como 'fallida' con razón 'cancelada por usuario'
    """

    def __init__(self, notificacion_repo: NotificacionRepositoryPort):
        self.notificacion_repo = notificacion_repo

    async def ejecutar(
        self,
        notificacion_id: int,
        usuario_id: int,
    ) -> None:
        """Cancela una notificación programada.
        
        Args:
            notificacion_id: ID de la notificación
            usuario_id: Usuario que cancela
            
        Raises:
            NotificacionNoEncontrada: Si no existe o no pertenece al usuario
            NotificacionYaEnviada: Si ya fue enviada
        """
        # Obtener notificación
        notificacion = await self.notificacion_repo.obtener_por_id(notificacion_id)
        
        if not notificacion or notificacion.usuario_id != usuario_id:
            raise NotificacionNoEncontrada(notificacion_id)

        # Verificar que no haya sido enviada
        if notificacion.enviado:
            raise NotificacionYaEnviada(notificacion_id)

        # Marcar como fallida (cancelada)
        notificacion.marcar_fallido("Cancelada por el usuario")
        await self.notificacion_repo.guardar(notificacion)

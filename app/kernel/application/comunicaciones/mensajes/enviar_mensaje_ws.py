from app.infrastructure.db.uow import UnitOfWork
from app.infrastructure.db.repositories.comunicaciones.mensajes_repo import MensajesRepository
from app.kernel.application.comunicaciones.mensajes.enviar_mensaje import EnviarMensajeUseCase
from app.infrastructure.ws.manager import ws_manager
from app.infrastructure.ws.events import WSChatMessagePayload, build_chat_message_event

class EnviarMensajeConWSService:
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    async def ejecutar(
        self,
        *,
        conversacion_id: int,
        remitente_id: int,
        texto: str,
    ) -> int:
        async with self.uow:
            repo = MensajesRepository(self.uow.session_required)
            uc = EnviarMensajeUseCase(repo)
            mensaje = await uc.ejecutar(
                conversacion_id=conversacion_id,
                remitente_id=remitente_id,
                texto=texto,
            )
            await self.uow.commit()

        payload = WSChatMessagePayload(
            mensaje_id=mensaje.id,
            conversacion_id=mensaje.conversacion_id,
            remitente_id=mensaje.remitente_id,
            texto=mensaje.texto,
            enviado_en=mensaje.enviado_en.isoformat(),
        )
        event = build_chat_message_event(payload)

        # De momento: solo al remitente. Luego, cuando uses participantes,
        # aquí iterarás sobre todos los user_id de la conversación.
        await ws_manager.send_to_user(remitente_id, event)

        return mensaje.id

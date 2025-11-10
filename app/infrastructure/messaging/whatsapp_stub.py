# app/infrastructure/messaging/whatsapp_stub.py
from __future__ import annotations
from datetime import datetime, timezone

class WhatsappStubService:
    async def send_text(self, to_e164: str, text: str) -> str:
        #Envio y devuelve un id determinista
        ts = int(datetime.now(timezone.utc).timestamp())
        return f"stub:{to_e164}:{ts}"

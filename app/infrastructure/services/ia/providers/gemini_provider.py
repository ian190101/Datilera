from __future__ import annotations

import logging

from google import genai
from google.genai import types

from app.config.settings import get_settings
from app.kernel.domain.ia.ia import IAProviderPort, IARequest, IAResponse


class GeminiProvider(IAProviderPort):
    """Adaptador asíncrono para el SDK oficial y vigente google-genai."""

    def __init__(self) -> None:
        settings = get_settings()
        self.api_key = settings.GEMINI_API_KEY
        self.default_model = settings.gemini_model

    def get_nombre_proveedor(self) -> str:
        return "gemini"

    async def generar_respuesta(self, request: IARequest) -> IAResponse:
        try:
            history = [
                types.Content(
                    role="user" if message.role == "user" else "model",
                    parts=[types.Part(text=message.content)],
                )
                for message in request.messages
                if message.role != "system"
            ]
            config = types.GenerateContentConfig(
                system_instruction=request.system_instruction,
                temperature=request.temperature,
                max_output_tokens=request.max_tokens,
            )

            async with genai.Client(api_key=self.api_key).aio as client:
                if history:
                    chat = client.chats.create(
                        model=self.default_model,
                        history=history,
                        config=config,
                    )
                    response = await chat.send_message(request.prompt)
                else:
                    response = await client.models.generate_content(
                        model=self.default_model,
                        contents=request.prompt,
                        config=config,
                    )

            usage = response.usage_metadata
            prompt_tokens = int(getattr(usage, "prompt_token_count", 0) or 0)
            response_tokens = int(getattr(usage, "candidates_token_count", 0) or 0)
            total_tokens = int(getattr(usage, "total_token_count", 0) or prompt_tokens + response_tokens)

            return IAResponse(
                content=response.text or "",
                model_name=self.default_model,
                tokens_prompt=prompt_tokens,
                tokens_response=response_tokens,
                tokens_total=total_tokens,
                # El precio no se fija en código porque varía por modelo y fecha.
                cost_usd=0.0,
                successful=True,
            )
        except Exception as exc:
            logging.exception("Error al generar una respuesta con Gemini")
            return IAResponse(
                content="",
                model_name=self.default_model,
                successful=False,
                error_message=str(exc),
            )

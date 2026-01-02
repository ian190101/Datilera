import google.generativeai as genai
from app.kernel.domain.ia.ia import IAProviderPort, IARequest, IAResponse, IAMessage
from app.config.settings import get_settings
import logging

settings = get_settings()

class GeminiProvider(IAProviderPort):
    def __init__(self):
        # Configurar API Key (Asegúrate de tener GEMINI_API_KEY en tu .env)
        if hasattr(settings, "GEMINI_API_KEY"):
            genai.configure(api_key=settings.GEMINI_API_KEY)
        else:
            logging.warning("GEMINI_API_KEY no encontrada en settings")
            
        # Modelo por defecto (flash es rápido y barato para MCP)
        self.default_model = "gemini-2.5-flash"

    def get_nombre_proveedor(self) -> str:
        return "gemini"

    async def generar_respuesta(self, request: IARequest) -> IAResponse:
        try:
            # 1. Configurar Modelo
            # Mapeamos 'system' role a system_instruction si existe
            system_inst = request.system_instruction
            
            # Gemini usa una configuración específica para system instruction
            model = genai.GenerativeModel(
                model_name=self.default_model,
                system_instruction=system_inst
            )

            # 2. Construir Historial
            # Convertimos el formato estándar IAMessage al formato de Gemini
            chat_history = []
            for msg in request.messages:
                role = "user" if msg.role == "user" else "model"
                chat_history.append({"role": role, "parts": [msg.content]})

            # 3. Iniciar Chat o Generar Contenido
            if chat_history:
                chat = model.start_chat(history=chat_history)
                response = await chat.send_message_async(request.prompt)
            else:
                response = await model.generate_content_async(request.prompt)

            # 4. Calcular Tokens (Estimado o real si la API lo devuelve)
            # Gemini devuelve usage_metadata
            usage = response.usage_metadata
            t_prompt = usage.prompt_token_count if usage else 0
            t_resp = usage.candidates_token_count if usage else 0
            
            # Costo aproximado Gemini 1.5 Flash (ajustar según precios vigentes)
            # Entrada: $0.075 / 1M tokens | Salida: $0.30 / 1M tokens
            cost = (t_prompt * 0.075 / 1_000_000) + (t_resp * 0.30 / 1_000_000)

            return IAResponse(
                content=response.text,
                model_name=self.default_model,
                tokens_prompt=t_prompt,
                tokens_response=t_resp,
                tokens_total=t_prompt + t_resp,
                cost_usd=cost,
                successful=True
            )

        except Exception as e:
            logging.error(f"Error en Gemini Provider: {str(e)}")
            return IAResponse(
                content="",
                model_name=self.default_model,
                successful=False,
                error_message=str(e)
            )
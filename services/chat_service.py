import json
from fastapi.responses import StreamingResponse
from openai import OpenAI
import logging
from typing import List, Dict, Any
from enum import Enum
from config import DEEPSEEK_API_KEY

# Configuración de logging
logger = logging.getLogger(__name__)

# Configuración del modelo
class ModelProvider(str, Enum):
    DEEPSEEK = "deepseek"

class ModelConfig:
    def __init__(self, model_id: str, api_key: str, base_url: str):
        self.model_id = model_id
        self.api_key = api_key
        self.base_url = base_url

# Configuración de DeepSeek
DEEPSEEK_MODEL_CONFIG = ModelConfig(
    model_id="deepseek-chat",
    api_key=DEEPSEEK_API_KEY,
    base_url="https://api.deepseek.com"
)

async def handle_chat_stream(client, messages: List[Dict[str, Any]]):
    async def generate():
        try:
            response = client.chat.completions.create(
                model=DEEPSEEK_MODEL_CONFIG.model_id,
                messages=messages,
                stream=True
            )

            accumulated_content = ""
            for chunk in response:
                if chunk.choices and chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    accumulated_content += content
                    yield f"data: {json.dumps({'content': content, 'status': 'streaming'})}\n\n"

                if chunk.choices and chunk.choices[0].finish_reason == "stop":
                    yield f"data: {json.dumps({'content': accumulated_content, 'status': 'done'})}\n\n"
                    break

        except Exception as e:
            logger.error(f"Error in generate(): {e}")
            yield f"data: {json.dumps({'status': 'error', 'message': str(e)})}\n\n"
    
    return generate()

async def handle_chat(messages: List[Dict[str, Any]]):
    client = OpenAI(
        api_key=DEEPSEEK_MODEL_CONFIG.api_key, 
        base_url=DEEPSEEK_MODEL_CONFIG.base_url
    )
    
    try:
        # Filtrar mensajes válidos
        valid_messages = [msg for msg in messages if msg.get("content")]
        
        # Generar stream de respuesta
        stream_generator = await handle_chat_stream(client, valid_messages)
        
        return StreamingResponse(stream_generator, media_type="text/event-stream")
    
    except Exception as e:
        logger.error(f"Error in handle_chat: {str(e)}")
        
        async def error_stream(error):
            yield f"data: {json.dumps({'status': 'error', 'message': str(error)})}\n\n"
        
        return StreamingResponse(error_stream(e), media_type="text/event-stream")

import os
from dotenv import load_dotenv

load_dotenv()

# API Keys and Configuration
DATABASE_URL = os.getenv("DATABASE_URL")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

DEEPSEEK_BASE_URL="https://api.deepseek.com/v1"

class ModelConfig:
    def __init__(self, model_id: str, api_key: str, base_url: str):
        self.model_id = model_id
        self.api_key = api_key
        self.base_url = base_url

# Configuración de DeepSeek
DEEPSEEK_MODEL_CONFIG = ModelConfig(
    model_id="deepseek-chat",
    api_key=DEEPSEEK_API_KEY,
    base_url=DEEPSEEK_BASE_URL
)

# Logging Configuration
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
}
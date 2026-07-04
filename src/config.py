"""Configuración cargada desde variables de entorno (.env)."""
import os
from dotenv import load_dotenv


class Config:
    def __init__(self):
        load_dotenv()

        self.telegram_bot_token = self._get_required_env('TELEGRAM_BOT_TOKEN')

        self.gemini_api_key = self._get_required_env('GEMINI_API_KEY')
        self.gemini_model = os.getenv('GEMINI_MODEL', 'gemini-3.5-flash')

        # Registro abierto por defecto (vacío) -- igual que Larry/Coco.
        allowed_ids_str = os.getenv('ALLOWED_USER_IDS', '')
        self.allowed_user_ids = [
            int(uid.strip()) for uid in allowed_ids_str.split(',') if uid.strip()
        ]

        self.log_level = os.getenv('LOG_LEVEL', 'INFO')
        self.log_dir = os.getenv('LOG_DIR', 'logs')

        self.db_path = os.getenv('DB_PATH', 'conceptos.db')

    def _get_required_env(self, key: str) -> str:
        value = os.getenv(key)
        if not value:
            raise ValueError(f"Variable de entorno {key} es requerida")
        return value

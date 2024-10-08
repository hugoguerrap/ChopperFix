import os

class Config:
    # Leer la API key de OpenAI desde las variables de entorno
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

    @staticmethod
    def validate_config():
        if not Config.OPENAI_API_KEY:
            raise ValueError("La API key de OpenAI no está configurada. Por favor, establece la variable de entorno 'OPENAI_API_KEY'.")

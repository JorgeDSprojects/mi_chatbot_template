import yaml  
from pathlib import Path  
from pydantic_settings import BaseSettings  
from dotenv import load_dotenv

import yaml
from pathlib import Path
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# 1. Cargar las variables de entorno (.env) de manera segura
load_dotenv()

# --- NUEVO: Contrato para la interfaz ---
class AppSettings(BaseSettings):
    title: str = "Chatbot Modular" # Valor por defecto por si se borra del YAML
    description: str = ""
    theme: str = "default"
    use_streaming: bool = True

# --- Contrato que ya teníamos para el LLM ---
class LLMSettings(BaseSettings):
    provider: str
    model_name: str
    temperature: float
    max_tokens: int = 1000

class AppConfig:
    def __init__(self):
        # 3. Encontrar el archivo config.yaml dinámicamente
        current_dir = Path(__file__).resolve().parent
        project_root = current_dir.parent.parent
        config_path = project_root / "config.yaml"
        
        # 4. Leer el YAML
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config_data = yaml.safe_load(f)
        except FileNotFoundError:
            raise Exception(f"No se encontró el archivo de configuración en: {config_path}")
        
        # 5. Validar y mapear AMBAS secciones
        self.llm = LLMSettings(**config_data.get("llm", {}))
        self.app = AppSettings(**config_data.get("app", {})) # <- ¡ESTA ES LA LÍNEA QUE FALTABA!

# 6. Instancia global (Singleton)
settings = AppConfig()
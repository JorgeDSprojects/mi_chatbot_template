import yaml  
from pathlib import Path  
from pydantic_settings import BaseSettings  
from dotenv import load_dotenv

# 1. Cargar las variables de entorno (.env) de manera segura  
load_dotenv()

# 2. Definir el "Contrato" de configuración con Pydantic  
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
          
        # 5. Validar y mapear la configuración (¡Ojo a los ** aquí!)
        self.llm = LLMSettings(**config_data.get("llm", {}))

# 6. Instancia global (Singleton) - ESTO ES LO QUE FALTABA
settings = AppConfig()
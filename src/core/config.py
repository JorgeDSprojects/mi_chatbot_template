import yaml  
from pathlib import Path  
from pydantic_settings import BaseSettings  
from dotenv import load_dotenv

# 1\. Cargar las variables de entorno (.env) de manera segura  
# Esto cargará tus API Keys en la memoria del sistema sin exponerlas en el código  
load_dotenv()

# 2\. Definir el "Contrato" de configuración con Pydantic  
class LLMSettings(BaseSettings):  
    provider: str  
    model_name: str  
    temperature: float

class AppConfig:  
    def __init__(self):  
        # 3\. Encontrar el archivo config.yaml dinámicamente  
        current_dir = Path(__file__).resolve().parent  
        project_root = current_dir.parent.parent  
        config_path = project_root / "config.yaml"  
          
        # 4\. Leer el YAML  
        try:  
            with open(config_path, "r", encoding="utf-8") as f:  
                config_data = yaml.safe_load(f)  
        except FileNotFoundError:  
            raise Exception(f"No se encontró el archivo de configuración en: {config_path}")  
          
        # 5\. Validar y mapear la configuración  
        self.llm = LLMSettings(config_data.get("llm", {}))
# **Fase 3: El Núcleo (src/core/)**

Llegamos al corazón de nuestra aplicación. Como en todo proyecto serio de software, aquí es donde van las configuraciones y las factorías. **Todo lo demás en el proyecto dependerá de esta carpeta.**

Vamos a construir los dos archivos fundamentales que leerán nuestras variables (del .env y el config.yaml) de forma segura, y el componente encargado de instanciar nuestro modelo de IA evitando el temido *Vendor Lock-in*.

## **3.1. La Configuración Central (config.py)**

Dentro de tu proyecto, navega a la carpeta src/core/ y crea un archivo llamado config.py.

Abre ese nuevo archivo y pega el siguiente código. A diferencia de los scripts tradicionales que leen diccionarios a mano, usaremos pydantic-settings para validar que nuestro YAML es correcto antes de que el programa arranque:


```
import yaml
from pathlib import Path
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# 1. Cargar las variables de entorno (.env) de manera segura
# Esto cargará tus API Keys en la memoria del sistema sin exponerlas en el código
load_dotenv()

# 2. Definir el "Contrato" de configuración con Pydantic
class LLMSettings(BaseSettings):
    provider: str
    model_name: str
    temperature: float

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
        
        # 5. Validar y mapear la configuración
        self.llm = LLMSettings(**config_data.get("llm", {}))

# 6. Instancia global (Singleton)
settings = AppConfig()
```


\# 6\. Instancia global (Singleton)  
settings \= AppConfig()

### **🧠 Análisis del Tutor: ¿Por qué lo hacemos así?**

1. **Seguridad y Modularidad (load\_dotenv):** Al llamar a load\_dotenv(), le decimos a Python: *"Ve al archivo .env, toma mi OPENAI\_API\_KEY y cárgala en secreto"*. De este modo, LangChain (y LangSmith) la encontrarán automáticamente más adelante.  
2. **Rutas Robustas (pathlib):** En lugar de escribir rutas frágiles como "../../config.yaml", usamos Path. Esto evita que tu aplicación explote dependiendo de si la ejecutas en tu portátil o en los servidores de Hugging Face.  
3. **El Patrón "Singleton" Simple (settings \= AppConfig()):** Al final del archivo creamos una instancia llamada settings. En el futuro, simplemente haremos: from src.core.config import settings en cualquier parte del proyecto, y podremos usar settings.llm.model\_name con autocompletado en nuestro editor, asegurando que el archivo YAML se lee una sola vez.

## **3.2. La Fábrica de LLMs (llm\_factory.py)**

Aquí es donde empezamos a aplicar verdadera ingeniería de software a la IA.

El **Patrón Factory** (Fábrica) es un concepto clásico. En lugar de esparcir código de OpenAI por todos tus archivos de Gradio o de agentes, creamos un único "departamento" cuya única responsabilidad es leer tu configuración y devolver el modelo ya ensamblado.

Crea el archivo src/core/llm_factory.py y copia este código:


```
from langchain_openai import ChatOpenAI
from src.core.config import settings

def get_llm():
    """
    Función Factory encargada de instanciar el modelo de lenguaje correcto 
    basándose en la configuración central.
    """
    # Leemos el proveedor desde nuestro config.yaml validado
    provider = settings.llm.provider.lower()

    if provider == "openai":
        # Instanciamos el modelo de OpenAI
        # Nota: No le pasamos la API Key explícitamente porque load_dotenv() ya lo hizo por debajo
        return ChatOpenAI(
            model=settings.llm.model_name,
            temperature=settings.llm.temperature
        )
        
    elif provider == "anthropic":
        # Ejemplo de cómo añadiríamos Anthropic (Claude) en el futuro
        # from langchain_anthropic import ChatAnthropic
        # return ChatAnthropic(
        #     model_name=settings.llm.model_name, 
        #     temperature=settings.llm.temperature
        # )
        raise NotImplementedError("El proveedor Anthropic se implementará más adelante.")
        
    elif provider == "ollama":
        # Ejemplo de cómo añadiríamos Ollama para modelos locales
        # from langchain_community.chat_models import ChatOllama
        # return ChatOllama(
        #     model=settings.llm.model_name, 
        #     temperature=settings.llm.temperature
        # )
        raise NotImplementedError("El proveedor Ollama se implementará más adelante.")
        
    else:
        raise ValueError(f"Proveedor LLM no soportado o desconocido: {provider}")
```


### **🧠 Análisis del Tutor: Diseccionando la Fábrica**

1. **El decorador @staticmethod:** Utilizamos esto para poder llamar a LLMFactory.create\_llm() directamente sin necesidad de instanciar la clase entera cada vez. Es una forma limpia y directa de "pedir" nuestro modelo.  
2. **Centralización de LangChain (Cero Vendor Lock-in):** Nota que ChatOpenAI se importa *solo* en este archivo. Ningún otro archivo en la carpeta src/chains/ o la interfaz de Gradio va a saber que estamos usando OpenAI. Ellos simplemente recibirán un "cerebro" genérico.  
3. **Testabilidad:** Si mañana quieres hacer pruebas automáticas sin gastar dinero en la API de OpenAI, solo tienes que modificar ligeramente esta fábrica para que devuelva un "Mock LLM" (un modelo de mentira) cuando detecte que estás ejecutando un test.  
4. **Preparado para el futuro:** He dejado comentados los espacios para Anthropic y Ollama. Cuando quieras cambiar a Claude, simplemente instalas su librería con uv, descomentas esas líneas y cambias la palabra "openai" a "anthropic" en tu config.yaml. El resto de tu aplicación ni se enterará del cambio.

Con este componente, el núcleo de tu aplicación está formalmente completo y blindado. El siguiente paso es crear nuestra **Lógica de Negocio (chains/)** y conectarla de forma limpia a **Gradio**.
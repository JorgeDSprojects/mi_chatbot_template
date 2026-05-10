Me pongo el sombrero de Arquitecto de Soluciones y de tu tutor. Excelente iniciativa. Crear este tutorial como documentación central de un *template* (plantilla) es exactamente como trabajan los equipos de Ingeniería de Plataformas (Platform Engineering). Permite que cualquier desarrollador junior de tu equipo se descargue el repositorio y empiece a programar con buenas prácticas desde el minuto cero.

Aquí tienes el plan del tutorial y, a continuación, el desarrollo completo paso a paso.

---

### 🗺️ Plan del Tutorial: De Cero a Producción

1. **Fase 1: Andamiaje y Entorno.** Creación de la estructura de carpetas (el esqueleto completo, aunque dejemos partes vacías por ahora) y gestión de dependencias.
2. **Fase 2: Configuración Híbrida (`.env` + `yaml`).** Cómo separar los secretos (API Keys) de los parámetros de comportamiento (modelos, temperaturas).
3. **Fase 3: El Núcleo (`src/core/`).** Construcción de nuestra `llm_factory.py` para instanciar OpenAI con observabilidad de LangSmith inyectada automáticamente.
4. **Fase 4: La Lógica de Negocio (`src/chains/`).** Creación de una cadena conversacional simple usando LangChain Expression Language (LCEL).
5. **Fase 5: La Interfaz y el Router (`src/interfaces/` y `app.py`).** Cómo montar la UI con Gradio y conectarla a nuestra cadena sin acoplar el código.
6. **Fase 6: Despliegue en Hugging Face Spaces.** Instrucciones para subir el código y configurar los *Secrets* en la plataforma.

---

# 📖 Tutorial: Construyendo un Chatbot Escalable con LangChain y Gradio

Bienvenido a la plantilla base para proyectos de IA. Este tutorial te guiará para levantar un chatbot sencillo conectado a OpenAI, pero utilizando una arquitectura de grado de producción.

## Fase 1: Andamiaje y Entorno

Primero, vamos a crear el esqueleto de nuestro proyecto. Abre tu terminal y ejecuta estos comandos para crear las carpetas, incluso aquellas que no usaremos hoy, para mantener la arquitectura intacta:

```bash
mkdir -p mi_chatbot_template/src/{core,interfaces,schemas,prompts,chains,tools,agents,rag}
mkdir -p mi_chatbot_template/data/{raw,vector_db,few_shots}
mkdir -p mi_chatbot_template/tests/{unit,integration}
cd mi_chatbot_template

```


### 1. Inicializar el proyecto con `uv`
En lugar de crear un entorno virtual manualmente o escribir un `requirements.txt` a mano, vamos a dejar que `uv` orqueste todo como un proyecto moderno.

Ejecuta el siguiente comando para inicializar el proyecto[cite: 2]:
```bash
uv init
```
*Nota del tutor:* Esto creará automáticamente tu archivo `pyproject.toml`[cite: 1]. Si `uv` genera un archivo `hello.py` por defecto como plantilla, puedes eliminarlo con tranquilidad, ya que nosotros usaremos el `main.py` que creamos en el paso anterior.

### 2. Añadir las dependencias
Ahora vamos a instalar nuestras herramientas esenciales para la interfaz, los frameworks de IA y la gestión de configuración. Al usar `uv`, estas dependencias se añadirán y bloquearán automáticamente en tu proyecto.

Ejecuta este comando para instalar las dependencias[cite: 2]:
```bash
uv add chainlit langchain langchain-openai python-dotenv pyyaml
```
Verás que es exageradamente más rápido que `pip`. Al hacer esto, `uv` también se encarga de crear el entorno virtual de forma silenciosa e instalar todo allí.

*(Tip adicional: Si en el futuro necesitas migrar un `requirements.txt` antiguo a este nuevo sistema con `pyproject`, recuerda que puedes usar el comando `uv add -r requirements.txt`[cite: 2]).*

### 3. Opciones de Ejecución
De cara a los siguientes módulos donde empezaremos a programar, tu guía nos da dos alternativas excelentes para trabajar:

*   **Para tener la terminal lista (Activación):** Si vas a trabajar un buen rato y prefieres tener el entorno activo, puedes activar el VENV[cite: 2]:
    ```cmd
    .venv\Scripts\activate
    ```
*   **La vía moderna (Ejecución directa):** Una de las grandes ventajas de `uv` es que te permite ejecutar código sin inicializar VENV explícitamente en la consola[cite: 2]. Cuando programemos nuestra interfaz en Chainlit, podremos usar `uv run`[cite: 2], delegando la gestión del entorno a la herramienta.

Con esto, nuestra base (Módulo 1.2) queda configurada a nivel profesional. Tienes una arquitectura limpia y una gestión de paquetes ultrarrápida.

```text
langchain-openai
langchain
gradio
pydantic-settings
pyyaml
python-dotenv

```

Instálalas: `pip install -r requirements.txt`

## Fase 2: Configuración Híbrida (`.env` + `yaml`)

La regla de oro de la arquitectura: **Los secretos no se suben a Git. Los parámetros sí.**

1. Abre el archivo `.env` y añade tus credenciales (asegúrate de que `.env` está en tu `.gitignore`):

```env
OPENAI_API_KEY="sk-tu-clave-aqui"

# Observabilidad con LangSmith
LANGCHAIN_TRACING_V2="true"
LANGCHAIN_API_KEY="lsv2-tu-clave-aqui"
LANGCHAIN_PROJECT="tutorial_chatbot_v1"

```

2. Abre `config.yaml` y define los parámetros del modelo. Esto permite cambiar el comportamiento sin tocar el código Python:

```yaml
llm:
  provider: "openai"
  model_name: "gpt-4o-mini"
  temperature: 0.7

```

## Fase 3: El Núcleo (`src/core/`)

Aquí reside la inteligencia para leer la configuración y levantar el modelo.

Crea el archivo `src/core/config.py`. Usaremos `pydantic-settings` para validar que nuestro YAML y nuestro `.env` están correctos:

```python
# src/core/config.py
import yaml
from pydantic_settings import BaseSettings
from pydantic import Field
from dotenv import load_dotenv

load_dotenv() # Carga el .env automáticamente

class LLMSettings(BaseSettings):
    provider: str
    model_name: str
    temperature: float

class AppConfig:
    def __init__(self, config_path: str = "config.yaml"):
        with open(config_path, "r") as f:
            config_data = yaml.safe_load(f)
        
        self.llm = LLMSettings(**config_data["llm"])

# Instancia global para usar en toda la app
settings = AppConfig()

```

Crea el archivo `src/core/llm_factory.py`. Esta es la fábrica que devuelve el modelo listo para usar. Gracias a las variables de entorno que pusimos en el `.env`, **LangSmith ya está monitorizando todo automáticamente** sin necesidad de añadir código extra aquí.

```python
# src/core/llm_factory.py
from langchain_openai import ChatOpenAI
from src.core.config import settings

def get_llm():
    """Devuelve la instancia del LLM basada en config.yaml"""
    if settings.llm.provider == "openai":
        return ChatOpenAI(
            model=settings.llm.model_name,
            temperature=settings.llm.temperature
        )
    else:
        raise ValueError(f"Proveedor {settings.llm.provider} no soportado aún.")

```

## Fase 4: La Lógica de Negocio (`src/chains/`)

No vamos a acoplar Gradio con OpenAI directamente. Vamos a crear una "Cadena" (Chain) que recibe texto y devuelve texto.

Crea el archivo `src/chains/chat_chain.py`:

```python
# src/chains/chat_chain.py
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from src.core.llm_factory import get_llm

def get_chat_response(user_message: str, history: list) -> str:
    """
    history: lista de tuplas [(user_msg, ai_msg), ...] que Gradio maneja.
    Para este bot simple, obviaremos el historial complejo y responderemos al mensaje actual,
    pero dejamos la firma preparada para el futuro.
    """
    llm = get_llm()
    
    # Un prompt muy básico. (En un proyecto real, esto iría en src/prompts/)
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Eres un asistente útil, directo y claro. Respondes siempre en español."),
        ("human", "{input}")
    ])
    
    # LCEL (LangChain Expression Language)
    chain = prompt | llm | StrOutputParser()
    
    return chain.invoke({"input": user_message})

```

## Fase 5: La Interfaz (`src/interfaces/` y `app.py`)

Ahora encapsulamos la interfaz de Gradio en su propio módulo.

Crea el archivo `src/interfaces/gradio_app.py`:

```python
# src/interfaces/gradio_app.py
import gradio as gr
from src.chains.chat_chain import get_chat_response

def build_ui():
    """Construye y devuelve la interfaz de Gradio."""
    
    # Usamos ChatInterface que ya gestiona el estado y el historial visualmente
    demo = gr.ChatInterface(
        fn=get_chat_response,
        title="Chatbot Modular (Plantilla)",
        description="Un bot simple construido con LangChain, listo para producción.",
        theme="soft"
    )
    return demo

```

**El punto de entrada:** Hugging Face Spaces (y muchos otros servicios) buscan por defecto un archivo llamado `app.py` en la raíz del proyecto. Nuestro `app.py` será un simple enrutador (router) estúpido que no tiene lógica, solo arranca la app.

Abre el `app.py` en la raíz de tu proyecto:

```python
# app.py
from src.interfaces.gradio_app import build_ui

# Construimos la interfaz
demo = build_ui()

# Lanzamos el servidor
if __name__ == "__main__":
    demo.launch()

```

## Fase 6: Despliegue en Hugging Face Spaces

Tu código es ahora un monolito modular perfectamente estructurado. Para subirlo a Hugging Face:

1. Ve a [Hugging Face Spaces](https://huggingface.co/spaces) y crea un nuevo Space.
2. Selecciona **Gradio** como SDK.
3. Antes de subir el código, ve a la pestaña **Settings** de tu Space.
4. Busca la sección **Variables and secrets**.
5. Añade tus secretos (¡Lo que tenías en tu `.env` local no se sube!):
* `OPENAI_API_KEY` = `sk-...`
* `LANGCHAIN_API_KEY` = `lsv2-...`
* `LANGCHAIN_TRACING_V2` = `true`
* `LANGCHAIN_PROJECT` = `hf_space_prod`


6. Sube tus archivos (puedes arrastrarlos en la UI de HF o usar Git):
* `/src/` (toda la carpeta)
* `app.py`
* `config.yaml`
* `requirements.txt`




Hugging Face instalará automáticamente tu `requirements.txt`, ejecutará `app.py`, leerá el `config.yaml` para saber que tiene que usar `gpt-4o-mini`, instanciará el LLM, y todas tus conversaciones quedarán perfectamente registradas en tu dashboard de LangSmith.
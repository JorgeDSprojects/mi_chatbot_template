Me pongo la bata de **Arquitecto de Soluciones** y **Tutor RAG**. Esta es una pregunta de nivel *Senior*. Entender la diferencia entre Batch (no-stream) y Streaming es lo que separa a quienes hacen demos de quienes hacen sistemas que soportan miles de usuarios en producción.

Vamos a dividir esto en dos partes: la teoría (el porqué) y la práctica (el cómo implementarlo de forma elegante en tu arquitectura).

---

### Parte 1: Streaming vs. Batch (No-Stream)

A nivel de funcionamiento y recursos, la diferencia es abismal.

#### 1. Modo Batch (No-Stream / Síncrono)

* **Cómo funciona:** El usuario hace la petición. El servidor llama a OpenAI. OpenAI genera el token 1, 2, 3... hasta el 1000. Todo esto se guarda en la memoria RAM de tu servidor. Cuando OpenAI termina, empaqueta los 1000 tokens y los envía de golpe al usuario en un solo bloque (JSON).
* **El problema del TTFB (Time to First Byte):** Si el LLM tarda 15 segundos en generar la respuesta, el usuario se queda mirando una pantalla congelada 15 segundos. En UX, esto es la muerte.
* **El problema de Infraestructura (Timeouts):** Si despliegas esto en AWS, Azure o incluso Hugging Face, los balanceadores de carga (Nginx, ALB) suelen tener un límite de espera por defecto (ej. 30 o 60 segundos). Si el servidor no devuelve *nada* en ese tiempo, el balanceador corta la conexión y lanza un terrible `504 Gateway Timeout`.

#### 2. Modo Streaming (Asíncrono / Chunks)

* **Cómo funciona:** El usuario hace la petición. El servidor abre una tubería HTTP especial llamada **SSE (Server-Sent Events)**. En cuanto OpenAI escupe el token 1, tu servidor lo empuja por la tubería hacia el navegador del usuario. Luego el 2, luego el 3.
* **Ventaja de UX:** El TTFB (Time to First Byte) cae a milisegundos. El usuario ve cómo el texto aparece al instante, dándole la sensación de que el bot "piensa rápido".
* **Ventaja de Infraestructura:** Como los tokens están viajando constantemente por la tubería de red, el balanceador de carga ve que "hay tráfico en vivo" y **no corta la conexión por timeout**, incluso si la respuesta total tarda 2 minutos en generarse.
* **La gran desventaja (El reto del Arquitecto):** Si le pides al LLM que te devuelva un JSON estructurado (ej. para extraer datos de una factura), en modo Streaming recibirás JSON rotos (`{"nombre": "Ju`... `an"}`). Parsear un JSON incompleto en tiempo real es un dolor de cabeza técnico (aunque existen herramientas para ello).

---

### Parte 2: El Interruptor en la Arquitectura (Toggle Feature)

Como buenos ingenieros, no vamos a reescribir la app. Vamos a crear una solución en la que **el archivo `config.yaml` decida** qué método usar.

#### Paso 1: Actualizar `config.yaml`

Añadimos nuestro interruptor en la sección `app`. Abre tu archivo y déjalo así:

```yaml
# config.yaml
app:
  title: "Chatbot Modular"
  description: "Un bot simple construido con LangChain, listo para producción."
  theme: "default"
  use_streaming: true   # <--- NUESTRO INTERRUPTOR MÁGICO

llm:
  provider: "openai"
  model_name: "gpt-4o-mini"
  temperature: 0.7
  max_tokens: 1000

```

#### Paso 2: Actualizar el Contrato en `src/core/config.py`

Le decimos a Pydantic que espere este nuevo valor booleano. Abre el archivo y añade el campo `use_streaming` a la clase `AppSettings`:

```python
# src/core/config.py (Solo el bloque modificado)
class AppSettings(BaseSettings):
    title: str = "Chatbot Modular" 
    description: str = ""
    theme: str = "default"
    use_streaming: bool = True  # <--- NUEVO CONTRATO

```

#### Paso 3: La magia en la Cadena (`src/chains/chat_chain.py`)

Aquí vamos a usar un truco de Python muy elegante. Python permite que una función sea un "Generador" si usa la palabra clave `yield`. Si el flag dice "stream", haremos un bucle emitiendo cada token. Si dice "batch", pediremos la respuesta completa con `.invoke()` pero haremos `yield` una sola vez para que Gradio no se rompa.

```python
# src/chains/chat_chain.py
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableSerializable
from src.core.llm_factory import get_llm
from src.prompts.chat_prompts import get_system_prompt

def build_chat_chain() -> RunnableSerializable:
    llm = get_llm()
    prompt = get_system_prompt()
    parser = StrOutputParser()
    return prompt | llm | parser

def get_chat_response(user_message: str, streaming: bool):
    """
    Recibe el mensaje y el booleano para decidir cómo procesar.
    Siempre devuelve un generador (yield) para estandarizar la salida.
    """
    chain = build_chat_chain()
    
    if streaming:
        # MODO STREAMING: Escupimos token a token
        respuesta_acumulada = ""
        for chunk in chain.stream({"input": user_message, "chat_history": []}):
            respuesta_acumulada += chunk
            yield respuesta_acumulada 
    else:
        # MODO BATCH: Esperamos a que todo termine, y lo devolvemos de golpe
        respuesta_completa = chain.invoke({"input": user_message, "chat_history": []})
        yield respuesta_completa

```

#### Paso 4: Conectar el cable en `src/interfaces/gradio_app.py`

Finalmente, nuestra interfaz solo tiene que leer el `settings.app.use_streaming` y pasárselo a la cadena.

```python
# src/interfaces/gradio_app.py
import gradio as gr
from src.core.config import settings
from src.chains.chat_chain import get_chat_response

def build_ui():
    
    def predict(message, history):
        # Leemos el interruptor del config y se lo pasamos a la cadena
        yield from get_chat_response(message, streaming=settings.app.use_streaming)

    view = gr.ChatInterface(
        fn=predict,
        title=settings.app.title,
        description=settings.app.description,
        examples=["¿Cómo puedo mejorar mi arquitectura?", "¿Qué es LCEL?"],
        cache_examples=False
    )
    
    return view

```

### 🧪 Pruébalo tú mismo

1. Asegúrate de tener `use_streaming: true` en tu `config.yaml`.
2. Lanza el servidor con `uv run app.py` y haz una pregunta larga. Verás la máquina de escribir (SSE en acción).
3. Detén el servidor, cambia `use_streaming: false` en el `config.yaml` y vuelve a lanzar.
4. Haz la misma pregunta. Verás que se queda pensando un rato y de repente aparece todo el bloque de texto de golpe (Modo Batch clásico).

Acabas de implementar el patrón **"Feature Flag"** (Bandera de Funcionalidad) impulsado por configuración. Si esto fuera una empresa real y el equipo de producto te dijera: *"¡Apaga el streaming que hay un bug en el navegador Safari!"*, podrías arreglarlo en 5 segundos cambiando una palabra en un YAML sin tener que reprogramar la aplicación entera ni hacer un nuevo commit crítico.
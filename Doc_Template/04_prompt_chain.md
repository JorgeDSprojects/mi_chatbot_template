Me pongo de nuevo mi bata de **Tutor RAG**. Has tocado el punto que separa a un "hacker de prompts" de un verdadero **Ingeniero de Software de IA**.

En tu propuesta inicial de la Fase 4 estabas cometiendo un pecado capital: **hardcoding del prompt dentro de la función de la cadena**. Si el equipo de producto quiere cambiar el tono del bot de "asistente serio" a "tutor sarcástico", tendrían que entrar a tu código de lógica de negocio (`chains/`) para cambiar un string. Eso es inaceptable en producción.

Aprovechando que mencionaste la carpeta `data/` y los archivos adjuntos de tu proyecto anterior, vamos a remodelar esta fase aplicando **Desacoplamiento Triple**:

1. **Datos (`data/`):** Los textos base y ejemplos (few-shots).
2. **Prompts (`src/prompts/`):** La lógica de construcción de la plantilla.
3. **Cadenas (`src/chains/`):** La tubería (pipeline) que une todo.

Aquí tienes la propuesta de refinamiento para que tu documentación sea de nivel Senior.

---

### Módulo 1.4: Lógica de Negocio y Gestión de Prompts Decoplada

Para entender por qué hacemos este esfuerzo extra, observa cómo fluye la información en nuestra arquitectura antes de escribir el código:

Como puedes ver, la cadena es simplemente el "pegamento". Si cambiamos el archivo de datos, la cadena no se entera, pero el resultado cambia. Esto es lo que permite escalar.

---

### Paso 1: Definir los Datos (`data/system_prompts.yaml`)

En lugar de JSON, usaremos **YAML** para los prompts porque permite multilínea de forma mucho más limpia.

Crea el archivo `data/system_prompts.yaml`:

```yaml
# data/system_prompts.yaml
default:
  role: "Eres un tutor experto en IA y Arquitectura de Software."
  style: "Directo, técnico pero pedagógico. No eres complaciente."
  goals:
    - "Explicar el 'porqué' de las decisiones técnicas."
    - "Asegurar que el código siga patrones de diseño limpios."

```

---

### Paso 2: El Gestor de Prompts (`src/prompts/chat_prompts.py`)

Este archivo se encarga de leer el YAML y transformarlo en un objeto `ChatPromptTemplate` de LangChain.

```python
# src/prompts/chat_prompts.py
import yaml
from pathlib import Path
from langchain_core.prompts import ChatPromptTemplate

def get_system_prompt(prompt_id: str = "default") -> ChatPromptTemplate:
    # 1. Localizar y leer el archivo de datos
    current_dir = Path(__file__).resolve().parent
    data_path = current_dir.parent.parent / "data" / "system_prompts.yaml"
    
    with open(data_path, "r", encoding="utf-8") as f:
        prompts_data = yaml.safe_load(f)
    
    config = prompts_data.get(prompt_id, prompts_data["default"])
    
    # 2. Construir el System Message dinámicamente
    system_text = f"{config['role']} {config['style']} Objetivos: {', '.join(config['goals'])}"
    
    return ChatPromptTemplate.from_messages([
        ("system", system_text),
        ("placeholder", "{chat_history}"), # Preparado para memoria futura
        ("human", "{input}")
    ])

```

---

### Paso 3: La Cadena de Ejecución (`src/chains/chat_chain.py`)

Ahora nuestra cadena es **pura elegancia**. No tiene strings, solo lógica de conexión.

```python
# src/chains/chat_chain.py
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableSerializable
from src.core.llm_factory import get_llm
from src.prompts.chat_prompts import get_system_prompt

def build_chat_chain() -> RunnableSerializable:
    """
    Construye la cadena de chat usando LCEL.
    Se puede reutilizar en Gradio, FastAPI o CLI.
    """
    llm = get_llm()
    prompt = get_system_prompt() # Aquí podríamos pasarle un ID distinto desde config.yaml
    parser = StrOutputParser()
    
    # La tubería (Pipeline) LCEL
    return prompt | llm | parser

def get_chat_response(user_message: str) -> str:
    """Función de conveniencia para la interfaz (Gradio/Chainlit)"""
    chain = build_chat_chain()
    # Invocamos pasando el diccionario que el prompt espera
    return chain.invoke({"input": user_message, "chat_history": []})

```

---

### 🧠 Análisis del Tutor: ¿Qué hemos ganado con este "sobreesfuerzo"?

1. **Independencia de Roles:** Si el experto en contenido quiere cambiar las instrucciones del bot, solo toca el `.yaml` en la carpeta `data/`. No necesita saber Python ni entrar en `src/`.
2. **Preparado para Test de A/B:** Podrías tener un `default_v1` y un `default_v2` en tu YAML y cambiarlos desde el `config.yaml` de la raíz sin tocar el código de la cadena.
3. **Memoria Lista:** He añadido un `placeholder` para `{chat_history}`. Aunque ahora no lo usemos, tu arquitectura ya es compatible con bots que recuerdan conversaciones pasadas simplemente cambiando la forma en que invocas la cadena.

¿Te das cuenta de la diferencia? Tu versión anterior era un "script". Esta versión es una **Aplicación de Grado Empresarial**.

Para que visualices cómo interactúan estos componentes y cómo el lenguaje LCEL de LangChain conecta las piezas, he preparado este simulador interactivo de la "Tubería de Datos".

¿Qué te parece este enfoque? Si lo ves claro, el último paso es la **Fase 5**, donde crearemos la interfaz de Gradio en `src/interfaces/` y el archivo `app.py` de entrada, que ahora serán increíblemente cortos gracias a que toda la "suciedad" lógica está bien escondida en las carpetas que acabamos de crear.
# Arquitectura Escalable para Proyectos LLM y RAG**

La transición de un simple script (Prueba de Concepto) a un sistema de Producción escalable (preparado para AWS, Azure, o Hugging Face Spaces) requiere una arquitectura robusta. El objetivo de este diseño es lograr un **desacoplamiento total**: cero *vendor lock-in* (cambiar de OpenAI a Anthropic o local en minutos), cero *UI lock-in* (pasar de terminal a Gradio o a una API sin reescribir lógica) y un sistema altamente testeable.

A continuación, se detalla el patrón estándar de arquitectura modular.

### **1\. El Árbol de Directorios Definitivo**

En proyectos serios de Python enfocados en IA, separamos estrictamente la infraestructura, los datos y el código fuente (src/).

```
mi\_proyecto\_llm/  
├── .venv/                    \# Entorno virtual (gestionado por uv o pip)  
├── .env                      \# Secretos (API Keys de OpenAI, Pinecone, LangSmith) \- ¡IGNORADO EN GIT\!  
├── .gitignore                \# Archivos a excluir del control de versiones  
├── pyproject.toml / uv.lock  \# Gestión moderna de dependencias  
├── config.yaml               \# ⚙️ Topología del sistema (Chunks, Modelos, Proveedores)  
├── Dockerfile                \# 🐳 La llave para despliegues en AWS/Azure/HF Spaces  
├── .github/                    
│   └── workflows/            \# 🚀 CI/CD: Pipelines para tests y despliegues automáticos  
│  
├── data/                     \# 📦 GESTIÓN DE DATOS Y ESTADO  
│   ├── raw/                  \# PDFs, excels originales para tu RAG  
│   ├── vector\_db/            \# Persistencia local (ej. ChromaDB local)  
│   └── few\_shots/            \# \<-- Aquí van tus JSON/YAML de ejemplos para el LLM  
│  
├── tests/                    \# 🧪 RED DE SEGURIDAD  
│   ├── unit/                 \# Tests de tus parsers, schemas y factorías (rápidos, sin gastar API)  
│   └── integration/          \# Tests evaluando al LLM (con LangSmith)  
│  
└── src/                      \# ❤️ EL CORAZÓN DE LA APLICACIÓN  
    │  
    ├── interfaces/           \# 🔌 PUERTOS DE ENTRADA (Aislamiento de UI)  
    │   ├── cli\_app.py        \# Para probar rápido en consola  
    │   ├── gradio\_app.py     \# Interfaz visual rápida (Hugging Face Spaces)  
    │   └── api\_fastapi.py    \# El backend real si vas a microservicios  
    │  
    ├── core/                 \# ⚙️ CONFIGURACIÓN Y CONEXIONES (El núcleo)  
    │   ├── config.py         \# Lee y parsea config.yaml y .env  
    │   ├── llm\_factory.py    \# Patrón Factory: Devuelve el LLM según config  
    │   └── observability.py  \# Inicializa trazas (LangSmith, Datadog)  
    │  
    ├── schemas/              \# 📐 CONTRATOS DE DATOS  
    │   └── models.py         \# Clases Pydantic (UserQuery, AgentResponse)  
    │  
    ├── prompts/              \# 📝 TEXTOS COMO CÓDIGO  
    │   └── templates.py      \# Plantillas que inyectan los few\_shots de /data  
    │  
    ├── rag/                  \# 📚 DOMINIO DE CONOCIMIENTO (Opcional según proyecto)  
    │   ├── document\_loaders.py  
    │   ├── text\_splitters.py  
    │   └── retrievers.py  
    │  
    ├── tools/                \# 🛠️ CAPACIDADES EXTERNAS  
    │   └── web\_search.py     \# Funciones que los agentes pueden usar  
    │  
    ├── chains/               \# ⛓️ FLUJOS DETERMINISTAS  
    │   └── qa\_chain.py       \# Junta LLM \+ Prompt \+ RAG \+ Output Parser  
    │  
    └── agents/               \# 🧠 FLUJOS AUTÓNOMOS  
        └── supervisor.py     \# Lógica multi-agente, LangGraph, ruteos
```


### **2\. Infraestructura y Datos (Fuera de src/)**

* **config.yaml vs .env:** Nunca pongas secretos en config.yaml. El .env guarda tus *API Keys* (OpenAI, LangSmith). El config.yaml define el *comportamiento*: qué proveedor usar por defecto (provider: "openai"), qué tamaño de chunk usar para RAG (chunk\_size: 1024), o qué base de datos vectorial conectar.  
* **La carpeta data/few\_shots/:** **Respuesta a la duda común sobre JSON/YAML.** Nunca dejes ejemplos estáticos ("few-shots") directamente (hardcoded) en el código Python. Guárdalos en data/few\_shots/ejemplos.json. Esto permite que un analista modifique el comportamiento del bot sin tocar código ni requerir un nuevo despliegue.  
* **Dockerfile y CI/CD:** Son el pasaporte a producción. Un contenedor te asegura que el código funcionará igual en tu portátil, en Hugging Face Spaces o en un clúster de Kubernetes en AWS.

### **3\. Explicación de los Subdominios Lógicos en src/**

Cada carpeta en src/ tiene una responsabilidad única. Respetar estas fronteras evita el "código espagueti":

* **interfaces/:** El LLM no sabe si le habla a una persona o a un servidor. Esta capa recibe peticiones HTTP o clics en Gradio, los convierte a texto plano y llama a src/chains/. Así evitamos el *UI Lock-in*.  
* **core/:** El corazón. Aquí reside llm\_factory.py. Si mañana sale un modelo mejor, cambias 2 líneas aquí y todo el proyecto se actualiza.  
* **schemas/:** Aquí viven las clases de **Pydantic**. Definen la forma exacta en la que entran y salen los datos. Es vital para parsers estructurados y para validar los inputs del usuario antes de gastar tokens.  
* **prompts/:** En IA, los prompts son código. Deben estar versionados. Estas plantillas importan la lógica, recogen variables y leen de data/ si necesitan inyectar few-shots.  
* **rag/:** Un dominio propio. No mezcles la carga de PDFs o la búsqueda en bases de datos vectoriales con la lógica de conversación.  
* **tools/:** Herramientas aisladas (ej. buscar clima, consultar SQL) que el modelo ejecutará. Deben estar fuertemente tipadas usando los schemas.  
* **chains/ y agents/:** La lógica de negocio real. Las cadenas son tuberías rectas (entra A, sale B). Los agentes toman decisiones (evalúan A, usan la herramienta X, deciden que falta información, usan la herramienta Y, devuelven B).

### **4\. Por qué esta arquitectura es "A Prueba de Balas"**

Imagina que escribes un script de 500 líneas donde mezclas la llamada a la API de OpenAI, los prompts, el chat de Gradio y la lógica RAG. Si haces eso, sufrirás:

1. **Imposibilidad de Pruebas (Testabilidad):** Si quieres probar que tu cadena de resumen funciona, con el monolito gastarás dinero de OpenAI en cada ejecución. Con esta estructura, separas el modelo en core/, lo que permite inyectar un "Mock LLM" (un modelo de mentira gratuito) en la carpeta tests/.  
2. **Agilidad para Pivotar:** \* *¿Tu jefe quiere pasar de Gradio a una API REST?* No tocas LangChain. Solo creas api\_fastapi.py en interfaces/.  
   * *¿Quieres dejar OpenAI por Anthropic?* Vas a config.yaml, cambias la variable default\_provider y llm\_factory.py se encarga del resto.

Esta estructura no solo te prepara para el desarrollo actual, sino que evoluciona contigo sin necesidad de reescribir desde cero.
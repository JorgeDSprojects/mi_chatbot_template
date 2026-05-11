# **Módulo 1.3: Configuración Híbrida y Protección de Secretos**

Esta es la frontera entre un script de principiante y un proyecto profesional. Como vimos en la estructura de nuestro proyecto, nuestra meta principal es separar las reglas de negocio de la configuración del modelo para evitar el *Vendor Lock-in* y el acoplamiento de la interfaz.

Para lograr esto y asegurar nuestro código, necesitamos tres archivos clave: .env, .gitignore y config.yaml.

Vamos a configurarlos paso a paso.

### **1\. El archivo .env (Tus Secretos)**

El archivo .env (Environment) tiene un único propósito: guardar tus contraseñas, tokens y claves de API de manera segura. **Nunca** debes escribir una API Key directamente en tus archivos .py ni en tus YAML.

Abre el archivo .env que creaste en la raíz del proyecto y pega lo siguiente:

```

# Proveedores de LLM  
OPENAI_API_KEY="sk-tu-api-key-de-openai-aqui"

# Observabilidad y Trazabilidad (LangSmith)  
LANGCHAIN_TRACING_V2="true"  
LANGCHAIN_API_KEY="lsv2-tu-api-key-de-langsmith-aqui"  
LANGCHAIN_PROJECT="asistente_modular_v1"

```

*(Nota del tutor: Reemplaza el texto entre comillas con tus claves reales. LangSmith detectará estas variables automáticamente en todo el proyecto).*

### **2\. El archivo .gitignore (Tu Escudo Protector)**

De nada sirve poner tus claves en el .env si luego subes ese archivo a un repositorio público en GitHub o a Hugging Face Spaces. Los bots escanean repositorios buscando claves de OpenAI expuestas para robar saldo.

El .gitignore le dice a git qué archivos o carpetas **debe ignorar por completo**. Crea un archivo llamado .gitignore en la raíz de tu proyecto y añade lo siguiente:

\# Secretos y Entornos  
.env  
.venv/  
env/

\# Python-generated files
__pycache__/
*.py[oc]
build/
dist/
wheels/
*.egg-info

\# Datos locales (No subir bases vectoriales gigantes ni PDFs de clientes)  
data/raw/  
data/vector\_db/  
\*.sqlite3

\# Archivos de SO  
.DS\_Store  
Thumbs.db

**Regla de Oro:** Siempre que inicies un proyecto, el .gitignore es el primer archivo que debes configurar y verificar antes de hacer tu primer git commit.

### **3\. El archivo config.yaml (Tu Panel de Control)**

Si el .env guarda las llaves, el config.yaml es el volante de tu coche. Aquí definiremos el comportamiento de nuestra aplicación, logrando un sistema completamente modular que no dependa de si usamos Gradio, FastAPI o la consola.

Abre tu archivo config.yaml y pega esta estructura:


```
# 1\. Variables de Interfaz  
app:  
  title: "Asistente"  
  description: "Chatbot agnóstico preparado para producción."  
  theme: "soft"

# 2\. Variables del Motor LLM (Se leerán en src/core/llm\_factory.py)  
llm:  
  provider: "openai"           # Opciones futuras: "anthropic", "ollama"  
  model_name: "gpt-4o-mini"  
  temperature: 0.0             # 0.0 para respuestas precisas (RAG), 0.7+ para creatividad  
  max_tokens: 1000

# 3\. Variables de RAG (Para futuros módulos)  
rag:  
  chunk_size: 1024  
  chunk_overlap: 100  
  vector_db: "chroma"
```


#### **¿Por qué YAML y no JSON o un archivo Python?**

YAML es el estándar de la industria (usado en Kubernetes, Docker, GitHub Actions). Es extremadamente fácil de leer para los humanos. Imagina que en el futuro un Product Manager quiere probar el modelo gpt-4o; solo tendrá que abrir este archivo de texto, cambiar una línea y guardar, sin tocar jamás la lógica de Python de tu aplicación.

### **4\. Escenarios Avanzados: Múltiples Modelos y Peticiones Dinámicas**

En la vida real, los proyectos crecen. Es normal que quieras usar un modelo barato (gpt-4o-mini) para tareas sencillas y uno potente (claude-3.5-sonnet) para síntesis compleja.

Aquí es donde nuestro diseño modular brilla.

#### **Escenario A: Perfiles en el YAML**

Puedes transformar la sección llm de tu config.yaml en perfiles:


```
llm:  
  default\_profile: "fast"  
  profiles:  
    fast:  
      provider: "openai"  
      model\_name: "gpt-4o-mini"  
    powerful:  
      provider: "anthropic"  
      model\_name: "claude-3-5-sonnet-20240620"
```


Tu código leería el perfil necesario. Esto es ideal para tener un "botón de emergencia" si un proveedor se cae.

#### **Escenario B: Inyección Dinámica (Jerarquía de Prioridades)**

Si tu backend (src/interfaces/api\_fastapi.py) recibe una petición de otra app que dice: *"Para este usuario Premium, usa GPT-4o"*, tu sistema debe obedecer a la app y usar el YAML solo como plan B.

La lógica profesional funciona por **jerarquía de prioridades**:

1. **Prioridad 1 (Máxima):** Lo que diga la petición externa (parámetros inyectados en la función).  
2. **Prioridad 2 (Media):** Lo que diga el archivo config.yaml (tu configuración por defecto).  
3. **Prioridad 3 (Mínima):** Valores "quemados" (hardcoded) en el código.

---

#### Escenario B: El modelo viene de una App Externa (Dinámico)
Si tu RAG es un servicio (API) y otra aplicación (el frontend, un CRM, etc.) te dice: *"Oye, para este usuario específico usa este modelo"*, entonces el archivo `config.yaml` pasa a ser tu **Plan B (Fallback)**.

La lógica profesional funciona por **jerarquía de prioridades**:

1.  **Prioridad 1 (Máxima):** Lo que diga la petición de la App Externa (el "payload" del API).
2.  **Prioridad 2 (Media):** Lo que diga el archivo `config.yaml` (tu configuración por defecto).
3.  **Prioridad 3 (Mínima):** Valores "quemados" (hardcoded) en el código como última instancia.


### **5\. El "Cerebro" de la operación: llm\_factory.py**

Para manejar todas estas prioridades sin ensuciar el código, usamos el **Patrón Factory** en src/core/llm\_factory.py. Imagina que este archivo es un recepcionista inteligente:

1. Recibe una instrucción: *"Quiero iniciar una cadena de chat"*.  
2. Busca en el config.yaml qué modelo está puesto por defecto.  
3. Busca en el .env la API Key necesaria para ese proveedor.  
4. Te entrega el objeto del LLM listo para usar en tu src/chains/.

Si mañana decides que el modelo por defecto ya no es de OpenAI, sino uno de Google, **solo cambias una línea en tu YAML** y todas tus cadenas y agentes empezarán a usar el nuevo modelo automáticamente.
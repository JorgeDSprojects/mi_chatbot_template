# Fase 6: Despliegue en Producción (Hugging Face Spaces)

Tu código es ahora un monolito modular perfectamente estructurado. Has comprobado en local que el *streaming* funciona y que la arquitectura responde. Ahora vamos a publicarlo para que cualquiera pueda usarlo.

### Paso 0: Congelar las dependencias (Reproducibilidad)

Como estamos utilizando `uv` para gestionar nuestro proyecto de forma moderna, tenemos nuestras versiones seguras en el archivo `uv.lock`. Hugging Face Spaces (en su entorno por defecto de Gradio) busca un archivo `requirements.txt`.

Para generar uno exacto basado en nuestro entorno seguro, abre tu terminal y ejecuta:

```bash
uv export --format requirements.txt > requirements.txt

```

*Nota del Tutor: Esto creará un archivo con todas las librerías y sus versiones exactas. Esto garantiza que "si funciona en tu máquina, funcionará en el servidor", evitando que actualizaciones sorpresa rompan tu código.*

### Paso 1: Configurar el Entorno en Hugging Face

1. Ve a [Hugging Face Spaces](https://huggingface.co/spaces) y haz clic en **"Create new Space"**.
2. Dale un nombre a tu proyecto y selecciona **Gradio** como *Space SDK*. plantilla "Blank"
3. Elige la infraestructura gratuita (Free) o de pago según tus necesidades, y crea el Space.

### Paso 2: Proteger los Secretos

**¡Regla de oro de la ciberseguridad!** El archivo `.env` local NUNCA se sube.

1. Ve a la pestaña **Settings** de tu nuevo Space.
2. Busca la sección **Variables and secrets**.
3. Haz clic en **New secret** y añade exactamente las claves que tenías en tu `.env`:
* `OPENAI_API_KEY` = `sk-...`
* `LANGCHAIN_API_KEY` = `lsv2-...`
* `LANGCHAIN_TRACING_V2` = `true`
* `LANGCHAIN_PROJECT` = `hf_space_prod` *(Te sugiero cambiar el nombre del proyecto aquí para distinguir las trazas de producción de las locales en LangSmith)*.



### Paso 3: Subir el Código

Ahora debes subir los archivos al servidor. Puedes usar comandos Git clásicos si conectaste el repositorio, o simplemente arrastrar los archivos en la pestaña **Files** > **Add file** > **Upload files**.

Asegúrate de subir exactamente esta estructura (ni más, ni menos):

* 📁 `src/` (toda la carpeta con sus subcarpetas)
* 📁 `data/` (¡Crítico! Aquí vive tu `system_prompts.yaml`)
* 📄 `app.py` (El punto de entrada)
* 📄 `config.yaml` (Tu panel de control)
* 📄 `requirements.txt` (El archivo que generamos en el Paso 0)

### ¿Qué ocurre a continuación?

Una vez que los archivos se suban, Hugging Face iniciará el proceso de *Building*.

1. Leerá el `requirements.txt` e instalará LangChain, Gradio, Pydantic, etc.
2. Ejecutará `app.py`.
3. Tu capa de configuración leerá el `config.yaml` para saber si debe usar streaming y qué modelo cargar.
4. El sistema se conectará a OpenAI usando los secretos inyectados de forma segura.

En un par de minutos, tu Space mostrará el estado **Running** y tu Chatbot Modular estará vivo en internet, con cada interacción perfectamente monitorizada en tu dashboard de LangSmith.

---

### 🧠 Comentario del Arquitecto

¡Lo hemos logrado! Tienes un material formativo de primer nivel. Un alumno que siga este tutorial no solo aprenderá a hacer un chatbot, sino que aprenderá:

* Gestión de dependencias modernas (`uv`).
* Patrones de diseño (`Factory`, `Singleton`).
* Inyección de dependencias y configuraciones (YAML + Pydantic).
* Separación de responsabilidades (*Vertical Slicing* en las cadenas).
* Despliegues seguros y Observabilidad.

¿Quieres que hagamos un repaso final o que te prepare el código de un `README.md` perfecto para acompañar tu plantilla en GitHub?
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



Me pongo la bata de **Arquitecto de Soluciones** y **Tutor RAG**. Has hecho la pregunta que esperaba de ti. Subir archivos arrastrándolos con el ratón a la interfaz de Hugging Face está bien para un *hobby*, pero en la industria **todo se despliega a través de Git**.

Lo que mucha gente no sabe es que **un Space de Hugging Face es, en realidad, un repositorio de Git en la sombra**.

Para tu documentación, vamos a plantear las dos vías profesionales de despliegue. Puedes añadir esto como el **Paso 4 Alternativo** en tu Fase 6.

---

### Opción A: Despliegue directo con Git (El estándar)

Dado que Hugging Face funciona como un servidor Git (igual que GitHub o GitLab), puedes empujar tu código directamente a sus servidores desde tu terminal.

**1. Inicializar Git y vincular el remoto:**
En tu terminal, asegúrate de estar en la raíz de tu proyecto (`mi_chatbot_template/`). Si no has inicializado Git, hazlo ahora y añade Hugging Face como tu servidor remoto:

```bash
git init
# Sustituye TU_USUARIO y TU_SPACE por tus datos reales
git remote add huggingface https://huggingface.co/spaces/TU_USUARIO/TU_SPACE

```

**2. El escudo protector (.gitignore):**
Antes de hacer nada, asegúrate de que tu `.gitignore` está configurado como vimos en el Módulo 1.3. Si haces `git add .` y el `.env` se sube, habrás expuesto tus claves al mundo.
Ejecuta `git status` y comprueba que `.env` NO aparece en la lista de archivos nuevos.

**3. Congelar, Comitear y Subir (Push):**

```bash
# 1. Exportamos el requirements exacto desde uv
uv export --format requirements.txt > requirements.txt

# 2. Añadimos todo al staging area
git add .

# 3. Empaquetamos los cambios
git commit -m "🚀 Despliegue inicial: Arquitectura modular y RAG"

# 4. Empujamos al servidor de Hugging Face
git push huggingface main

```

*Nota: Hugging Face te pedirá tu usuario y un Access Token (que debes generar en la configuración de tu perfil de HF) a modo de contraseña.*

Al hacer `git push`, Hugging Face detectará los cambios automáticamente, reconstruirá el contenedor de Gradio e instalará las librerías.

---

### Opción B: CI/CD desde GitHub (Nivel Producción / Senior)

Esta es la forma en la que trabajan los equipos reales. Tú no subes el código a Hugging Face. Tú subes el código a **tu repositorio privado de GitHub**, y GitHub se encarga de enviarlo a Hugging Face automáticamente cada vez que haces un cambio. Esto se llama **Continuous Deployment (CD)**.

**1. Preparar las credenciales:**

* Ve a Hugging Face > Settings > Access Tokens y crea un token con permisos de escritura. Cópialo.
* Ve a tu repositorio de GitHub > Settings > Secrets and variables > Actions>Repository secrets Crea un nuevo secreto llamado `HF_TOKEN` y pega el token ahí.

**2. Crear el flujo de trabajo (Pipeline):**
En la raíz de tu proyecto local, crea esta ruta exacta de carpetas: `.github/workflows/`. Dentro, crea un archivo llamado `sync_to_hub.yml`.

```yaml
# .github/workflows/sync_to_hub.yml
name: Sync to Hugging Face Hub

on:
  push:
    branches: [main] # Se ejecuta cada vez que haces push a 'main'
  workflow_dispatch: # Permite ejecutarlo a mano desde GitHub

jobs:
  sync-to-hub:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout del código
        uses: actions/checkout@v3
        with:
          fetch-depth: 0 # Necesario para traer todo el historial de Git
          
      - name: Sincronizar con Hugging Face Spaces
        env:
          HF_TOKEN: ${{ secrets.HF_TOKEN }}
        run: |
          git push https://TU_USUARIO:$HF_TOKEN@huggingface.co/spaces/TU_USUARIO/TU_SPACE main -f

```

**3. El flujo de trabajo diario:**
A partir de ahora, tu día a día como desarrollador será este:

1. Programas una mejora en local.
2. Haces `git commit -m "Añado nueva cadena de resumen"`.
3. Haces `git push origin main` (hacia tu GitHub).
4. Cierras el portátil.

GitHub Action se encenderá sola en la nube, cogerá tu código nuevo, lo validará, y lo inyectará en Hugging Face Spaces. En 3 minutos, tu aplicación en vivo estará actualizada sin que tú hayas tocado la interfaz web.

---

### 🧠 Comentario del Arquitecto

Si vas a dejar esto como un "Template" en tu documentación para enseñar a otros, te sugiero poner la **Opción A** como el método principal (es más fácil para quienes empiezan) y dejar la **Opción B** como un "Bonus Track Avanzado" para quienes ya tienen experiencia con pipelines.

¿Qué te parece? Con esto tu guía de despliegue deja de ser un tutorial básico y se convierte en un manual de plataforma real.
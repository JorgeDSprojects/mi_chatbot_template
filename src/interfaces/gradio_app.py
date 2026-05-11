# src/interfaces/gradio_app.py
# src/interfaces/gradio_app.py
import gradio as gr
from src.core.config import settings
from src.chains.chat_chain import get_chat_response

def build_ui():
    """
    Construye la interfaz de Gradio consumiendo la 
    configuración definida en config.yaml.
    """
    
    def predict(message, history):
        # Ignoramos el historial de momento
        return get_chat_response(message)

    # Configuramos la interfaz. Eliminamos el parámetro 'theme' 
    # por los *breaking changes* de la nueva versión de Gradio.
    view = gr.ChatInterface(
        fn=predict,
        title=settings.app.title,
        description=settings.app.description,
        examples=["¿Cómo puedo mejorar mi arquitectura?", "¿Qué es LCEL?"],
        cache_examples=False
    )
    
    return view

# src/interfaces/gradio_app.py
import gradio as gr
from src.core.config import settings
from src.chains.chat_chain import get_chat_response

def build_ui():
    """
    Construye la interfaz de Gradio consumiendo la 
    configuración definida en config.yaml.
    """
    
    # Función puente para adaptar el formato de Gradio a nuestra cadena
    def predict(message, history):
        # Por ahora ignoramos el historial, pero la firma lo requiere
        return get_chat_response(message)

    # Configuramos la interfaz usando nuestro objeto settings
    view = gr.ChatInterface(
        fn=predict,
        title=settings.app.title,
        description=settings.app.description,
        theme=settings.app.theme,
        examples=["¿Cómo puedo mejorar mi arquitectura?", "¿Qué es LCEL?"],
        cache_examples=False
    )
    
    return view

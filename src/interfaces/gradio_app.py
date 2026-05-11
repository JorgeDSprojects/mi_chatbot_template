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

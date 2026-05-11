# app.py
from src.interfaces.gradio_app import build_ui

# 1. Construimos la interfaz (que a su vez inicializa settings y la cadena)
demo = build_ui()

# 2. Ejecución
if __name__ == "__main__":
    # En producción (Hugging Face), launch() detecta automáticamente el puerto
    demo.launch()

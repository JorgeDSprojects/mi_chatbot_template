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

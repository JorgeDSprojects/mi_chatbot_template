# src/chains/chat_chain.py
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableSerializable
from src.core.llm_factory import get_llm
from src.prompts.chat_prompts import get_system_prompt

def build_chat_chain() -> RunnableSerializable:
    llm = get_llm()
    prompt = get_system_prompt()
    parser = StrOutputParser()
    return prompt | llm | parser

def get_chat_response(user_message: str, streaming: bool):
    """
    Recibe el mensaje y el booleano para decidir cómo procesar.
    Siempre devuelve un generador (yield) para estandarizar la salida.
    """
    chain = build_chat_chain()
    
    if streaming:
        # MODO STREAMING: Escupimos token a token
        respuesta_acumulada = ""
        for chunk in chain.stream({"input": user_message, "chat_history": []}):
            respuesta_acumulada += chunk
            yield respuesta_acumulada 
    else:
        # MODO BATCH: Esperamos a que todo termine, y lo devolvemos de golpe
        respuesta_completa = chain.invoke({"input": user_message, "chat_history": []})
        yield respuesta_completa

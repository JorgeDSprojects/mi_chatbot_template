from langchain_openai import ChatOpenAI
from src.core.config import settings

def get_llm():
    """
    Función Factory encargada de instanciar el modelo de lenguaje correcto 
    basándose en la configuración central.
    """
    # Leemos el proveedor desde nuestro config.yaml validado
    provider = settings.llm.provider.lower()

    if provider == "openai":
        # Instanciamos el modelo de OpenAI
        # Nota: No le pasamos la API Key explícitamente porque load_dotenv() ya lo hizo por debajo
        return ChatOpenAI(
            model=settings.llm.model_name,
            temperature=settings.llm.temperature
        )
        
    elif provider == "anthropic":
        # Ejemplo de cómo añadiríamos Anthropic (Claude) en el futuro
        # from langchain_anthropic import ChatAnthropic
        # return ChatAnthropic(
        #     model_name=settings.llm.model_name, 
        #     temperature=settings.llm.temperature
        # )
        raise NotImplementedError("El proveedor Anthropic se implementará más adelante.")
        
    elif provider == "ollama":
        # Ejemplo de cómo añadiríamos Ollama para modelos locales
        # from langchain_community.chat_models import ChatOllama
        # return ChatOllama(
        #     model=settings.llm.model_name, 
        #     temperature=settings.llm.temperature
        # )
        raise NotImplementedError("El proveedor Ollama se implementará más adelante.")
        
    else:
        raise ValueError(f"Proveedor LLM no soportado o desconocido: {provider}")
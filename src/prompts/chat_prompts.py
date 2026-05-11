# src/prompts/chat_prompts.py
import yaml
from pathlib import Path
from langchain_core.prompts import ChatPromptTemplate

def get_system_prompt(prompt_id: str = "default") -> ChatPromptTemplate:
    # 1. Localizar y leer el archivo de datos
    current_dir = Path(__file__).resolve().parent
    data_path = current_dir.parent.parent / "data" / "system_prompts.yaml"
    
    with open(data_path, "r", encoding="utf-8") as f:
        prompts_data = yaml.safe_load(f)
    
    config = prompts_data.get(prompt_id, prompts_data["default"])
    
    # 2. Construir el System Message dinámicamente
    system_text = f"{config['role']} {config['style']} Objetivos: {', '.join(config['goals'])}"
    
    return ChatPromptTemplate.from_messages([
        ("system", system_text),
        ("placeholder", "{chat_history}"), # Preparado para memoria futura
        ("human", "{input}")
    ])

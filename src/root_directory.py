from pathlib import Path

#Diretório root 
ROOT_DIRECTORY = Path(__file__).parents[0]


# Prompts.json
PROMPT_CHAT = ROOT_DIRECTORY / "prompts" / "chat.json"
PROMPT_STD_QUESTION = ROOT_DIRECTORY / "prompts" / "standalone_question.json"
PROMPT_VALIDATION = ROOT_DIRECTORY / "prompts" / "validation.json"


#Arquivo de perguntas  e respostas
QUESTIONS_DATA_PATH = ROOT_DIRECTORY / "doc" / "perguntas_chatbot.xlsx"


#Carregar coleção
CHROMA_DB = ROOT_DIRECTORY / "db"

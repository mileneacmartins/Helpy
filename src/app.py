import os
import json
import logging
import tiktoken
import pandas as pd
from dotenv import load_dotenv
from typing import Any, Optional
from langchain.chains import LLMChain
from chromadb import PersistentClient
from langchain.prompts import load_prompt
from langchain.chat_models import AzureChatOpenAI
from langchain.schema import AIMessage, HumanMessage
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
from langchain.memory import ConversationSummaryBufferMemory, ChatMessageHistory
from root_directory import PROMPT_CHAT, PROMPT_STD_QUESTION, CHROMA_DB, PROMPT_VALIDATION


class HelpyBot:
    def __init__(self):
        """
        Initialize the HelpyBot instance.
        """
        load_dotenv()

        self.embedding_function = OpenAIEmbeddingFunction(
            api_key=os.getenv("OPENAI_API_KEY"),
            api_base=os.getenv("OPENAI_API_BASE"),
            api_type="azure",
            api_version=os.getenv("OPENAI_API_VERSION"),
            model_name=os.getenv("EMBEDDING_DEPLOYMENT_NAME"),
        )

        self.llm = AzureChatOpenAI(
            openai_api_base=os.getenv("OPENAI_API_BASE"),
            openai_api_version=os.getenv("OPENAI_API_VERSION"),
            deployment_name=os.getenv("DEPLOYMENT_NAME"),
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            openai_api_type="azure",
        )

        self.memory = ConversationSummaryBufferMemory(
            llm=self.llm,
            memory_key="chat_history",
            chat_memory=ChatMessageHistory(),
            input_key="human_input",
            max_token_limit=500,
            human_prefix="HUMAN_INPUT",
            ai_prefix="AI",
        )

        self.collection = self.get_collection("apostila_python")

        self.prompt_chat = load_prompt(PROMPT_CHAT)
        self.prompt_std_question = load_prompt(PROMPT_STD_QUESTION)


    def get_collection(self, collection_name: str) -> Optional[Any]:
        """
        Obter a coleção com base no nome da coleção.

        Args:
            collection_name (str): O nome da coleção a ser recuperada.

        Returns:
            Optional[Any]: A coleção recuperada, se encontrada, caso contrário, None.
        """

        client = PersistentClient(path=str(CHROMA_DB))

        try:
            collection = client.get_collection(
                name=collection_name, embedding_function=self.embedding_function
            )
            logging.info(f"Coleção encontrada {collection_name}")
            return collection
        except:
            logging.error(f"Collection {collection_name} not found.")
            return None


    def format_chat_history(
        self,
        memory: ConversationSummaryBufferMemory,
        last_message: str = "",
        just_human: bool = False,
        array_mode: bool = False,
    ) -> str:
        """
        Formata o histórico de conversas com base na instância de memória e nas configurações de entrada.        

        Parameters
        ----------
        memory : ConversationSummaryBufferMemory
            Instância de memória
        last_message : str, optional
            Última mensagem do usuário, por padrão ""
        just_human : bool, optional
            Se as mensagens são apenas do usuário, por padrão False
        array_mode : bool, optional
            array_mode por padrão False

        Returns
        -------
        str
            Histórico de conversas formatado, seja como uma única string ou uma
            lista se array_mode for True.
        """

        messages_array = memory.chat_memory.messages
        messages_formated = []

        for messages in messages_array:
            if isinstance(messages, HumanMessage):
                messages_formated.append(f"{memory.human_prefix}: {messages.content}")

            elif not just_human and isinstance(messages, AIMessage):
                messages_formated.append(f"{memory.ai_prefix}: {messages.content}")

        messages_formated.append(f"{memory.human_prefix} {last_message}")

        if array_mode:
            return messages_formated

        return "\n".join(messages_formated)


    def num_tokens_from_string(
        self, string: str, encoding_name: str = "cl100k_base"
    ) -> int:
        """
        Retorna o número de tokens em uma string de texto.

        Parameters
        ----------
        string : str
            String a ser tokenizada.
        encoding_name : str
            Tipo de codificação, por padrão 'cl100k_base'

        Returns
        -------
        str
            Número de tokens em uma string fornecida.
        """
        encoding = tiktoken.get_encoding(encoding_name)
        num_tokens = len(encoding.encode(string))

        return num_tokens


    def assemble_context(
        self, query: str, collection: Any, filters: dict = {}, k: int = 10
    ) -> str:
        """
        Recupera o contexto para uma dada consulta, verificando se o número 
        de tokens está dentro do máximo para o modelo de LLM utilizado.
        
        Parameters
        ----------
        query : str
                Mensagem do usuário
        collection : Any
            A coleção a ser consultada.
        filters : dict
            Filtros para a consulta na coleção
        k : int
            Número de documentos a ser recuperado, por padrão 20
            
        Returns
        -------
        str
            Contexto completo para uma dada consulta
        """

        results = collection.query(
            query_texts=[query],
            n_results=k,
            where=filters,
        )

        contents = results["documents"][0]
        metadatas = results["metadatas"][0]
        context_list = []

        for i in range(k):
            context_str = (
                f"Capitulo: {metadatas[i]['Chapter']}\n"
                f"Seção: {metadatas[i]['Session']}\n"
                f"Contexto: {contents[i]}"
            )
            context_list.append(context_str)

        max_tokens = 3600
        tokens = None
        while (tokens is None) or (tokens > max_tokens):
            complete_context = "\n\n---------\n".join(context_list)
            tokens = self.num_tokens_from_string(complete_context)
            if tokens > max_tokens:
                context_list.pop()
                print("Último elemento removido da lista")

        return "\n\n---------\n".join(context_list)


    def get_standalone_question(
        self, query: str, memory: ConversationSummaryBufferMemory
    ) -> str:
        """
        Obtém a pergunta independente a partir de uma pergunta de acompanhamento em um chat.
        
        Parameters
        ----------
        query : str
            Mensagem do usuário
        memory : ConversationSummaryBufferMemory
            Memória da sessão atual
            
        Returns
        -------
        str
            Pergunta independente para o acompanhamento
        """
        chat_history = self.format_chat_history(memory=memory, last_message=query)
        chain = LLMChain(prompt=self.prompt_std_question, llm=self.llm, verbose=True)

        return chain.predict(chat_history=chat_history, human_input=query)


    def get_answer(
        self, query: str, content: str, memory: ConversationSummaryBufferMemory
    ) -> str:
        """
            Obtém a resposta para uma consulta.
        
        Parameters
        ----------
        query : str
            Mensagem do usuário
        memory : ConversationSummaryBufferMemory
            Memória da sessão atual
        content : str
            Conteúdo a ser usado para gerar a resposta
            
        Returns
        -------
        str
            Resposta ao usuário
        """
        chat_history = self.format_chat_history(memory=memory, last_message=query)
        chain = LLMChain(
            prompt=self.prompt_chat, llm=self.llm, verbose=True, memory=memory
        )

        response = chain.predict(
            content=content, chat_history=chat_history, human_input=query
        )

        return response
        

    def read_questions_and_answers(self, file_path: str):
        """
        Lê perguntas e respostas de um arquivo Excel e as retorna como uma lista de dicionários.
        """
        return pd.read_excel(file_path).to_dict("records")


    def chatbot_response_validation(self, questions_and_answers):
        """
        Valida as respostas do chatbot em relação a um conjunto de perguntas e respostas esperadas.
        """
        prompt_validation = (PROMPT_VALIDATION)
        validated_responses = []

        try:
            with open(prompt_validation, "r", encoding="utf-8") as file:
                prompt_data = json.load(file)
        except FileNotFoundError:
            return [{"question": qa["pergunta"], "validation": "Validation prompt file not found."} for qa in questions_and_answers]

        for qa in questions_and_answers:
            chatbot_response = self.chat(qa["pergunta"])
            validation_prompt = prompt_data["template"].format(
                question=qa["pergunta"],
                chatbot_response=chatbot_response,
                expected_answer=qa["resposta_referencia"],
            )

            classification = self.llm.predict(text=validation_prompt)
            validated_responses.append(
                {
                    "question": qa["pergunta"],
                    "chatbot_response": chatbot_response,
                    "expected_answer": qa["resposta_referencia"],
                    "classification": classification,
                }
            )

        return validated_responses



    def rank_count(self, validated_responses):
        """
        Conta os resultados da classificação e calcula a porcentagem de precisão.
        """
        classification_counts = {"Correto": 0, "Incorreto": 0}
        total_questions = len(validated_responses)

        for response in validated_responses:
            classification = response.get("classification", "Incorreto")
            if classification in ["Correto", "Parcialmente Correto"]:
                classification_counts["Correto"] += 1
            else:
                classification_counts["Incorreto"] += 1

        classification_counts["Porcentagem de Acertos"] = (classification_counts["Correto"] / total_questions * 100) if total_questions > 0 else 0

        return classification_counts


    def chat(self, query: str) -> str:
        """
            Sequência de chat de prompts e busca de contexto.
            
        Parameters
            ----------
            query : str
                Mensagem do usuário
            memory : ConversationSummaryBufferMemory
                Memória da sessão atual
                
        Returns
            -------
            str
                Resposta ao usuário
        """

        standalone_question = self.get_standalone_question(
            query=query, memory=self.memory
        )

        content = self.assemble_context(
            query=standalone_question, collection=self.collection
        )

        response = self.get_answer(query=query, memory=self.memory, content=content)

        return response



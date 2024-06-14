import streamlit as st
import time
from app import HelpyBot
from dotenv import load_dotenv
from root_directory import QUESTIONS_DATA_PATH
import random

if __name__ == "__main__":
    load_dotenv("../.env", override=True)

    st.set_page_config(page_title="HelpyBot", layout="wide")

    st.markdown("<h1 style='text-align: center;'>Helpy</h1>", unsafe_allow_html=True)
    st.markdown("🐍 Um Chatbot especializado na linguagem Python. Peça dicas sobre: Loops, Funções, Bibliotecas e muito mais...", unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)


    st.sidebar.markdown("<h1>Validação de acertos do Helpy</h1>", unsafe_allow_html=True)
    st.sidebar.markdown("Ao começar a validação, você iniciará um teste automático para verificar se o bot está respondendo conforme o esperado.")
    if st.sidebar.button("Iniciar validação"):
        helpybot = HelpyBot()
        questions_and_answers = helpybot.read_questions_and_answers(QUESTIONS_DATA_PATH)

        with st.spinner("Validando resposta, isso pode demorar alguns minutos..."):
            checked_answers = helpybot.chatbot_response_validation(questions_and_answers)

            response_stats = helpybot.rank_count(checked_answers)

            st.sidebar.write("-----")
            st.sidebar.subheader("Resultado da validação:")
            st.sidebar.markdown(f"Acertos: <span style='color: green;'>{response_stats['Correto']}</span>", unsafe_allow_html=True)
            st.sidebar.markdown(f"Erros: <span style='color: red;'>{response_stats['Incorreto']}</span>", unsafe_allow_html=True)
            if "Porcentagem de Acertos" in response_stats:
                st.sidebar.markdown(f"Porcentagem de Acertos: <span style='color: white; font-weight: bold;'>{response_stats['Porcentagem de Acertos']:.2f}%</span>", unsafe_allow_html=True)
            else:
                st.sidebar.markdown("Porcentagem de Acertos: <span style='color: white; font-weight: bold;'>Não disponível</span>", unsafe_allow_html=True)



    if "chatbot" not in st.session_state:
        st.session_state.chatbot = HelpyBot()

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.spinner("Buscando..."):
            chatbot_response = st.session_state.chatbot.chat(prompt)

        if chatbot_response is not None:
            with st.chat_message("assistant"):
                response_placeholder = st.empty()
                simulated_text = "" 
                for char in chatbot_response:
                    simulated_text += char
                    response_placeholder.markdown(simulated_text)
                    time.sleep(0.03)

            st.session_state.messages.append({"role": "assistant", "content": chatbot_response})


    st.sidebar.markdown("<hr>", unsafe_allow_html=True)


    game_question = {
    "Qual a palavra-chave usada para definir uma função em Python?": {
        "alternativas": ["def", "function", "method", "func"],
        "resposta_correta": "def"
    },
    "Como você pode gerar números aleatórios em Python?": {
        "alternativas": ["random.randint()", "math.rand()", "random.range()", "math.randomize()"],
        "resposta_correta": "random.randint()"
    },
    "Qual função é usada para imprimir algo na tela?": {
        "alternativas": ["echo()", "printf()", "write()", "print()"],
        "resposta_correta": "print()"
    },
    "Qual variável está nomeada corretamente?": {
        "alternativas": ["2things", "two_things", "TwoThings", "%things"],
        "resposta_correta": "two_things"
    },
    "Qual dessas opções é um tipo bool?": {
        "alternativas": ["'banana'", "34", "True", "[1, 2, 3]"],
        "resposta_correta": "True"
    },
    "O que faz o método pop()?": {
        "alternativas": [
            "Adiciona um item ao final da lista",
            "Remove o item na posição dada da lista e o retorna. Se nenhuma posição for especificada, remove e retorna o último item da lista",
            "Combina duas listas",
            "Ordena os itens da lista"
        ],
        "resposta_correta": "Remove o item na posição dada da lista e o retorna. Se nenhuma posição for especificada, remove e retorna o último item da lista"
    },
    "Qual é a saída de print(8 / 4)?": {
        "alternativas": ["2", "2.0", "8", "Erro"],
        "resposta_correta": "2.0"
    },
    "Qual a sintaxe correta para criar um dicionário em Python?": {
        "alternativas": [
            "d = ['key': 'value']",
            "d = {key: 'value'}",
            "d = ('key': 'value')",
            "d = <key: 'value'>"
        ],
        "resposta_correta": "d = {key: 'value'}"
    },
    "Como você pode capturar exceções em Python?": {
        "alternativas": ["try...catch", "try...finally", "try...except", "try...error"],
        "resposta_correta": "try...except"
    }
}

    st.sidebar.markdown("<h1>Game sobre Python</h1>", unsafe_allow_html=True)

    if 'current_question' not in st.session_state or st.sidebar.button("Tentar outra Pergunta"):
        st.session_state.current_question = random.choice(list(game_question.items()))

    question, question_data = st.session_state.current_question

    st.sidebar.markdown(question)
    user_response = st.sidebar.radio("Alternativas", question_data["alternativas"], key="quiz")

    if st.sidebar.button("Responder", key="submeter"):
        if user_response == question_data["resposta_correta"]:
            st.sidebar.success("Correto! 🎉")
        else:
            st.sidebar.error("Incorreto. 😢 Tente novamente!")

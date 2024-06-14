# Helpy
Helpy Chatbot - Assistente especializado na linguagem *Python*!

### Funcionalidades

- **ChatGPT 3.5 Utilizado:** Utilização da API da OpenAI para interações conversacionais.
  
- **Base de Dados:** Dados extraídos e tratados de um PDF com 220 páginas da Alura, abrangendo conteúdos e códigos sobre Python e Orientação a Objetos.

- **Validação de Respostas:** Implementação de um sistema de validação para melhorar a precisão das respostas fornecidas.

Este projeto abrange áreas como:

- Engenharia de Dados
- Ciência de Dados
- Engenharia de Prompt
- Engenharia de IA Generativa
- Desenvolvimento GPT

#

### Instalação

1. Clonar o repositório:
```bash
https://github.com/mileneacmartins/Helpy.git
```
2. Istalar dependências:
```bash
pip install -r requirements.txt
```
3. Providencie a chave de API da OpenAI e configure as variáveis de ambiente de acordo com o exemplo abaixo:
```bash
OPENAI_API_TYPE="azure"
OPENAI_API_KEY="exemplo012345exemplo"
OPENAI_API_BASE="https://exemplo.azure.com/"
OPENAI_API_VERSION="0000-00-00"
DEPLOYMENT_NAME="exemplo"
EMBEDDING_DEPLOYMENT_NAME="exemplo"
```
5. Executar a interface do bot:
```bash
streamlit run src/st.py
```

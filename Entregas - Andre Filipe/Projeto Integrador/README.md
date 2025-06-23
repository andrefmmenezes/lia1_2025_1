# Analisador de Áudios com IA

O projeto final de LIA1 é um webapp para análise de arquivos de áudio. A aplicação permite o upload de um áudio, que é transcrito utilizando o modelo Whisper da OpenAI. A identificação dos dos participantes no áudio (diarização) é realizada com o auxílio do modelo Gemini 2.5 Flash, que também é responsável por gerar resumos, extrair pontos-chave e sugerir tópicos para aprofundamento.

## ✨ Funcionalidades

*   **Upload Intuitivo:** Suporte para upload de arquivos de áudio por clique ou arrastando e soltando (drag-and-drop).
*   **Player de Áudio:** Player integrado para ouvir o áudio enviado.
*   **Transcrição com Whisper:** Utiliza o modelo `base` do Whisper da OpenAI para uma transcrição rápida e precisa.
*   **Diarização com Gemini:** A transcrição inicial é refinada pela API do Google Gemini para corrigir erros, formatar o texto e identificar diferentes interlocutores.
*   **Resumo do Áudio:** Gera um resumo conciso do conteúdo do áudio.
*   **Extração de Pontos-Chave:** Identifica e lista os principais assuntos discutidos no áudio, incluindo timestamps.
*   **Sugestão de Tópicos:** Oferece "pontos de partida" (perguntas e conceitos) para aprofundar a discussão sobre o tema.

## 🚀 Tecnologias Utilizadas

*   **Frontend:** HTML5, TailwindCSS, JS
*   **Backend:** Python 3, FastAPI
*   **IA & Machine Learning:**
    *   OpenAI Whisper
    *   Google Gemini
    *   PyTorch
*   **Containerização:** Docker

## 🚀 Execute o Projeto no Google Colab

Além das execuções direta e via Docker, é possível iniciar a aplicação no Colab, acessando o link abaixo: 

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1WLpwZZOVqyTQTa6AJXBd_GZYkEo-w3Jx?usp=sharing)


## ⚙️ Como Executar o Projeto com Docker

### Pré-requisitos para a Instalação via Docker

*   Docker
*   NVIDIA Container Toolkit (necessário para suporte a GPU)
*   Uma chave de API do **Google Gemini**.

### Passos para a Instalação via Docker

1.  **Clone o repositório:**
    ```bash
    git clone https://github.com/andrefmmenezes/lia1_2025_1.git
    cd lia1_2025_1/Entregas\ -\ Andre\ Filipe/Projeto\ Integrador/
    ```

2.  **Crie o arquivo de ambiente:**
    Crie um arquivo chamado `.env` na raiz do projeto.

3.  **Adicione sua chave da API:**
    Dentro do arquivo `.env`, adicione sua chave da API do Google Gemini:
    ```env
    GEMINI_API_KEY="SUA_CHAVE_API_AQUI"
    ```

4.  **Construa e execute o container Docker:**
    O projeto inclui um script para facilitar o processo. Dê permissão de execução e rode-o:
    ```bash
    chmod +x script.sh
    ./script.sh
    ```
    Este script irá:
    *   Construir a imagem Docker chamada `final_proj`.
    *   Parar e remover qualquer container antigo com o nome `final_proj_container`.
    *   Iniciar um novo container com suporte a GPU, mapeando a porta `8001` do seu host para a porta `8000` do container.

    **Importante:** Certifique-se de criar o arquivo `.env` **antes** de construir a imagem Docker, pois o comando `COPY . .` no `Dockerfile` o incluirá no contexto do build.

5.  **Acesse a aplicação:**
    Abra seu navegador e acesse: `http://localhost:8001`

## 📂 Estrutura do Projeto

```
.
├── app/
│   ├── api.py          # Define os endpoints da API com FastAPI.
│   └── services.py     # Contém a lógica de negócio (transcrição, chamadas ao Gemini).
├── static/
│   ├── index.html      # A página principal da aplicação.
│   └── main.js         # Lógica do frontend (uploads, chamadas de API, manipulação do DOM).
├── .dockerignore       # Arquivos não incluídos no build.
├── .env                # Arquivo com variáveis de ambiente (local, não versionado).
├── Dockerfile          # Define a imagem Docker para a aplicação.
├── main.py             # Ponto de entrada da aplicação FastAPI.
├── requirements.txt    # Dependências Python.
└── script.sh           # Script para build e execução do container.
```

## 🔌 Endpoints da API

A API está disponível sob o prefixo `/api`.

#### `POST /api/transcribe/`

*   **Corpo:** `multipart/form-data` com um arquivo de áudio no campo `file`.
*   **Resposta:** Retorna a transcrição original e a transcrição aprimorada pela IA.

#### `POST /api/summarize/`

*   **Corpo:** JSON com o campo `text` contendo a transcrição.
*   **Resposta:** Retorna um resumo do texto.

#### `POST /api/keypoints/`

*   **Corpo:** JSON com o campo `text` contendo a transcrição.
*   **Resposta:** Retorna uma lista de pontos-chave com timestamps.

#### `POST /api/suggestions/`

*   **Corpo:** JSON com o campo `text` contendo a transcrição.
*   **Resposta:** Retorna uma lista de tópicos sugeridos para aprofundamento.
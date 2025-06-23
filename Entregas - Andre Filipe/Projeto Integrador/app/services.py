import os
import json
from typing import List
from datetime import timedelta

import httpx
import dotenv
from fastapi import UploadFile
import shutil
import torch

dotenv.load_dotenv()
GEMINI_MODEL = "gemini-2.5-flash" # gemini-2.5-flash-lite-preview-06-17 # gemini-2.0-flash
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={os.getenv('GEMINI_API_KEY')}"

# Diretório para upload temporário dos audios
UPLOADS_DIR = "temp_dir"
os.makedirs(UPLOADS_DIR, exist_ok=True)


async def transcribe_audio_file(file: UploadFile, model) -> dict:
    """
    Salva um arquivo de áudio temporariamente, o transcreve usando Whisper e depois o deleta.
    """
    if file.filename is None:
        return {"detail": "Formato de arquivo inválido. Apenas arquivos de áudio são suportados."}
    
    file_path = os.path.join(UPLOADS_DIR, file.filename)
    try:
        # salva o conteúdo do upload no arquivo temporário
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # faz a transcrição usando o modelo Whisper
        result = model.transcribe(file_path, fp16=torch.cuda.is_available())
        text = ""
        for segment in result['segments']:
            start = str(timedelta(seconds=round(segment['start'])))
            end = str(timedelta(seconds=round(segment['end'])))
            text += f"[{start} - {end}] {segment['text']}\\n"
        
        return {
            "transcription": text,
            "ai_transcription": await generate_better_transcription(text)
        }

    except Exception as e:
        return {"detail": f"Erro ao transcrever o áudio: {str(e)}"}

    finally:
        # fecha arquivo do upload e remove o arquivo temporário
        file.file.close()
        if os.path.exists(file_path):
            os.remove(file_path)


async def generate_better_transcription(text: str) -> str:
    """
    Chama a API do Gemini para gerar um resumo do texto.
    """
    prompt =  f""""O seguinte texto é uma transcrição de um áudio. Melhore a transcrição seguindo estas instruções:
      1. Identifique a quantidade de interlocutes e, se for possível inferir, nomeie-os pelo nome deles ou função em português (por exemplo, "Entrevistador", "Entrevistado", "Cliente", etc.) 
      2. Corrija os erros de transcrição com base no contexto da conversa.
      3. Se a transcrição estiver em inglês, traduza-a para o ptBR, mantendo a tradução fiel ao conteúdo original.
      4. Após identificar os interlocutores e corrigir a transcrição, Retorne SOMENTE a transcrição final exatamente como no exemplo:
        [mm:ss - mm:ss] <b>Interlocutor 1:</b> fala dele até ser interrompido.
        <br>[mm:ss - mm:ss] <b>Entrevistador:</b> fala dele até ser interrompido.
      5. NÃO USE MARKDOWN, SOMENTE AS TAGS HTML "<b>" e "</b>" para o nome do interlocutor. USE "<br>" para quebra de linha.
      Texto original: ```{text}```"""
    return await gemini_generate_text(prompt)


async def generate_summary(text: str) -> str:
    """
    Prompt para chamar a API do Gemini para gerar um resumo do texto. 
    """
    prompt = f"""O seguinte texto é uma transcrição de um áudio. 
    1. Crie um resumo conciso e fluído em um único parágrafo.
    O texto para analisar é: ``{text}``"""
    
    return await gemini_generate_text(prompt)


async def generate_keypoints(text: str) -> List[dict]:
    """
    Extrai pontos-chave do texto usando a API do Gemini.
    """
    
    prompt = f"""O seguinte texto é uma transcrição de um áudio.
    1. liste exatamente 3 pontos-chave discutidos no texto.

    Cada ponto deve conter:
    - Um timestamp de início e fim no formato `[mm:ss - mm:ss]`.
    - Um ponto-chave do assunto abordado na transcrição, que deve ser conciso e direto.

    O texto para analisar é: ``{text}``"""

    # Schema para garantir que a resposta da API seja um JSON no formato correto
    response_schema = {
        "type": "ARRAY",
        "description": "Uma lista dos 3 tópicos chave discutidos no texto.",
        "items": {
            "type": "OBJECT",
            "properties": {
                "timestamp": {
                    "type": "STRING",
                    "description": "Uma string contendo o timestamp do ponto-chave."
                },
                "text": {
                    "type": "STRING",
                    "description": "O texto descritivo do ponto-chave."
                }
            },
            "required": ["timestamp", "text"]
        }
    }
    return await gemini_generate_object(prompt, response_schema)


async def generate_suggestions(text: str) -> List[dict]:
    """
    Chama a API do Gemini para extrair tópicos em formato JSON.
    """
    
    prompt = f"""O seguinte texto é uma transcrição de um áudio.
    Analise o texto e sugira 5 "Pontos de Partida". O objetivo é fornecer ao usuário ganchos para discutir o assunto ou se aprofundar nele.

    Para cada ponto, formule uma **pergunta-chave ou um conceito para explorar**. Evite apenas listar fatos.

    Cada ponto deve ter:
    - Uma breve descrição (até 100 caracteres).
    - Um emoji representativo.

    O texto é: ``{text}``"""

    # Schema para garantir que a resposta da API seja um JSON no formato correto
    response_schema = {
        "type": "ARRAY",
        "description": "Uma lista de 5 tópicos chave discutidos no texto.",
        "items": {
            "type": "OBJECT",
            "properties": {
                "icon": {
                    "type": "STRING",
                    "description": "Uma string contendo um emoji que represente o tópico."
                },
                "text": {
                    "type": "STRING",
                    "description": "O texto descritivo do tópico."
                }
            },
            "required": ["icon", "text"]
        }
    }
    return await gemini_generate_object(prompt, response_schema)


async def gemini_generate_text(prompt: str) -> str:
    """
    Chama a API do Gemini e retorna a resposta.
    """
    body = {
        "contents": [{
            "role": "user",
            "parts": [{"text": prompt}]
        }]
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(GEMINI_API_URL, json=body, timeout=120)
            response.raise_for_status() # Verifica se a resposta foi bem-sucedida
            result = response.json()
            summary = result['candidates'][0]['content']['parts'][0]['text']
            return summary.strip()
        except (httpx.RequestError, KeyError, IndexError) as e:
            print(f"Erro ao chamar a API: {e}")
            return "Não foi possível retornar um resultado neste momento."


async def gemini_generate_object(prompt: str, response_schema: dict) -> List[dict]:
    """
    Chama a API do Gemini para extrair objetos em formato JSON.
    """
    body = {
        "contents": [{
            "role": "user",
            "parts": [{"text": prompt}]
        }],
        "generationConfig": {
            "responseMimeType": "application/json",
            "responseSchema": response_schema
        }
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(GEMINI_API_URL, json=body, timeout=120)
            response.raise_for_status()
            result = response.json()
            object_str = result['candidates'][0]['content']['parts'][0]['text']
            return json.loads(object_str)
        except (httpx.RequestError, KeyError, IndexError, json.JSONDecodeError) as e:
            print(f"Erro ao chamar a API de tópicos: {e}")
            return [{"icon": "💀", "text": "Não foi possível gerar os tópicos. 😭"}]

import torch
import whisper
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.api import router as api_router

app = FastAPI(
    title="Analisador de Áudios", 
    description="API para transcrição e análise de áudio usando Whisper e Gemini", 
    version="1.0.0"
)


app.include_router(api_router, prefix="/api")
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.on_event("startup")
async def startup_event():
    """
    Carrega o modelo Whisper na inicialização do app.
    """
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Usando dispositivo: {device}")
    try:
        model = whisper.load_model("base", device=device)
        app.state.model = model
    except Exception as e:
        print(f"Erro ao carregar o modelo Whisper: {e}")


@app.get("/", response_class=FileResponse)
async def get_index_page():
    """
    Serve a página principal do app.
    """
    return FileResponse('static/index.html')


if __name__ == "__main__":
    print("Para iniciar o app, execute o comando no terminal:")
    print("uvicorn main:app --reload")

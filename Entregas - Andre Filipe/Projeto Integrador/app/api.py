from fastapi import File, UploadFile, Request, HTTPException, APIRouter

from . import services

router = APIRouter()

@router.post("/transcribe/")
async def transcribe_audio(request: Request, file: UploadFile = File(...)):
    model = request.app.state.model
    if not model:
        raise HTTPException(status_code=503, detail="Modelo Whisper não está disponível.")
    transcription = await services.transcribe_audio_file(file, model)
    if transcription.get("detail"):
        raise HTTPException(status_code=400, detail=transcription["detail"])
    return transcription


@router.post("/summarize/")
async def summarize_text(request: Request):
    data = await request.json()
    text = data.get("text")
    if not text:
        raise HTTPException(status_code=400, detail="Nenhum texto fornecido.")
    summary = await services.generate_summary(text)
    return {"summary": summary}


@router.post("/keypoints/")
async def get_keypoints(request: Request):
    data = await request.json()
    text = data.get("text")
    if not text:
        raise HTTPException(status_code=400, detail="Nenhum texto fornecido.")
    keypoints = await services.generate_keypoints(text)
    return {"keypoints": keypoints}

@router.post("/suggestions/")
async def get_suggestions(request: Request):
    data = await request.json()
    text = data.get("text")
    if not text:
        raise HTTPException(status_code=400, detail="Nenhum texto fornecido.")
    suggestions = await services.generate_suggestions(text)
    return {"suggestions": suggestions}

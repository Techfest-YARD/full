from fastapi import APIRouter, Query

from services.gemini_service import GeminiService

router = APIRouter(prefix="/upload", tags=["chat"])

gemini = GeminiService()

@router.post("/")
async def get_answer(prompt: str = Query(..., min_length=1)):
    answer = gemini.ask(prompt)
    return { "response": answer }

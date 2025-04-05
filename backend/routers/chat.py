from fastapi import APIRouter, Query

from services.gemini_service import GeminiService

router = APIRouter(prefix="/chat", tags=["chat"])

gemini = GeminiService()

@router.get("/")
async def get_answer(prompt: str = Query(..., min_length=1)):
    answer = gemini.ask(prompt)
    return { "response": answer }

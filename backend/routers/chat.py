from fastapi import APIRouter, Query
from services.gemini_service import GeminiService
import logging

router = APIRouter(prefix="/chat", tags=["chat"])
logger = logging.getLogger(__name__)

gemini = GeminiService()

@router.get("/")
async def get_answer(prompt: str = Query(..., min_length=1)):
    logger.info(f"📥 Received prompt: {prompt}")
    answer = await gemini.ask(prompt)
    logger.info(f"📤 Response: {answer[:200]}...")  # logujemy tylko pierwsze 200 znaków
    return {"response": answer}

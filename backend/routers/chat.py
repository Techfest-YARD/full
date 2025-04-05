from fastapi import APIRouter, Query
from services.gemini_service import GeminiService
from services.RagPipelineService import RagPipelineService
import logging

router = APIRouter(prefix="/chat", tags=["chat"])
logger = logging.getLogger(__name__)

gemini = GeminiService()
pipeline = RagPipelineService()

@router.get("/")
async def get_answer(prompt: str = Query(..., min_length=1)):
    answer = pipeline.run(prompt)
    return { "response": answer }

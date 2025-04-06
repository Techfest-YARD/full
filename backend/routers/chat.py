from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
from services.gemini_service import GeminiService
from services.RagPipelineService import RagPipelineService
import logging

from services.logger_service import LoggerService

router = APIRouter(prefix="/chat", tags=["chat"])
logger = logging.getLogger(__name__)

gemini = GeminiService()
logger = LoggerService()
pipeline = RagPipelineService(logger=logger)

@router.get("/")
async def get_answer(prompt: str = Query(..., min_length=1)):
    try:
        answer = pipeline.run(prompt)
        return {"response": answer}
    except Exception as e:
        # logger.exception("Error in default RAG mode")
        return JSONResponse(status_code=500, content={"error": str(e)})

@router.get("/curious_child")
async def curious_child_chat(prompt: str = Query(..., min_length=1)):
    try:
        answer = pipeline.run_curious_child(prompt)
        return {"response": answer}
    except Exception as e:
        # logger.exception("Error in curious_child RAG mode")
        return JSONResponse(status_code=500, content={"error": str(e)})
    
@router.get("/gemini/generate_topics")
async def curious_child_chat(prompt: str = Query(..., min_length=1)):
    try:
        answer = pipeline.generate_topics_from_context(prompt)
        return {"response": answer}
    except Exception as e:
        # logger.exception("Error in curious_child RAG mode")
        return JSONResponse(status_code=500, content={"error": str(e)})


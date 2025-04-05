from fastapi import APIRouter, Query
from services.gemini_service import GeminiService
import logging
import httpx
import logging

router = APIRouter(prefix="/test", tags=["test"])
logger = logging.getLogger(__name__)

@router.get("/")
async def test_internet():
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            logger.error("before response")
            response = await client.get("https://google.com")
            logger.error("after response")

            return {"status": response.status_code}
    except Exception as e:
        return {"error": str(e)}
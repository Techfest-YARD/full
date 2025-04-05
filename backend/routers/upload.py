from fastapi import APIRouter, Query


router = APIRouter(prefix="/upload", tags=["upload"])

@router.post("/")
async def upload_documents(prompt: str = Query(..., min_length=1)):
    return { "response": prompt }
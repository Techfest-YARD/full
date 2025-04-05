from fastapi import APIRouter, Query


router = APIRouter(prefix="/chat", tags=["chat"])

@router.get("/")
async def upload_documents(prompt: str = Query(..., min_length=1)):
    return { "response": prompt }
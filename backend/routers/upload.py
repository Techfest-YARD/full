from typing import List
from fastapi import APIRouter, File, Query, UploadFile

router = APIRouter(prefix="/upload_documents", tags=["upload"])

@router.post("/")
async def upload_documents(files: List[UploadFile] = File(...)):
    file_names = [file.filename for file in files]
    
    return {"received_files": file_names}

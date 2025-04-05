from fastapi import APIRouter, Query


router = APIRouter(prefix="/upload", tags=["upload"])

@router.post("/process")
async def upload_documents(files: List[UploadFile] = File(...)):
    file_names = [file.filename for file in files]
    # Tu możesz np. zapisać pliki albo przetworzyć
    return {"received_files": file_names}
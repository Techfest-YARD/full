from typing import List
from fastapi import APIRouter, File, Query, UploadFile
from services.VectorStoreRetrainer import VectorStoreRetrainer
from services.UploadPdfService import PdfSaver


router = APIRouter(prefix="/upload_documents", tags=["upload"])
pdf_saver = PdfSaver()
vectorstore_retrainer = VectorStoreRetrainer()

@router.post("/")
async def upload_documents(files: List[UploadFile] = File(...)):
    file_names = [file.filename for file in files]
    
    await pdf_saver.upload_pdfs(files)

    

    return {"received_files": file_names}

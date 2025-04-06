from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from requests import Session
import sqlalchemy
import httpx
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from fastapi import UploadFile, File
from typing import List
import sqlalchemy
from sqlalchemy import text
import time
from dotenv import load_dotenv
import os
from sqlalchemy.sql import text

# Załóżmy, że plik z tekstem
load_dotenv()
loader = TextLoader("xd.txt")
documents = loader.load()
VECTOR_PASSWORD = os.getenv("VECTOR_PASSWORD")



def connect_via_public_ip() -> sqlalchemy.engine.base.Engine:
    """
    Tworzy połączenie z PostgreSQL (np. w Cloud SQL) przez publiczny IP,
    używając SQLAlchemy + psycopg2.
    """
    host = "35.246.200.139"      # publiczny IP bazy
    port = 5432
    db_user = "postgres"
    db_pass = VECTOR_PASSWORD
    db_name = "postgres"

    connection_url = f"postgresql+psycopg2://{db_user}:{db_pass}@{host}:{port}/{db_name}"
    engine = sqlalchemy.create_engine(connection_url)
    return engine

class PdfSaver:
    async def save_pdf_to_db(self, db_session: Session, filename: str, file_data: bytes):
        # Assuming you have a table 'documents' already created in PostgreSQL
        query = text("""
    INSERT INTO pdf_files (file_name, file_data) 
    VALUES (:filename, :file_data)
    """)
        db_session.execute(query, {"filename": filename, "file_data": file_data})
        db_session.commit()

    async def upload_pdfs(self, files: list[UploadFile]):
        # Connect to the database
        engine = connect_via_public_ip()
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()

        for file in files:
            # Read the file data into bytes
            file_data = await file.read()

            # Save the file to the database
            await self.save_pdf_to_db(db, file.filename, file_data)

        db.close()

        return {"message": "Files uploaded successfully"}

        
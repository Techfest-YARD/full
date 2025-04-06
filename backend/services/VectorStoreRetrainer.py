from dotenv import load_dotenv
import numpy as np
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
import fitz  # PyMuPDF
from langchain.text_splitter import RecursiveCharacterTextSplitter
from markdownify import markdownify as md
import os
import sqlalchemy
from sqlalchemy import text
from langchain.embeddings import HuggingFaceEmbeddings

# Załóżmy, że plik z tekstem
load_dotenv()

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

async def get_all_documents(self, db_session: AsyncSession):
    # Query all documents from the 'pdf_files' table
    query = select([text('file_name'), text('file_data')]).select_from(text('pdf_files'))
    result = await db_session.execute(query)
    documents = result.fetchall()

    markdown_documents = []

    # Convert each PDF document into markdown text
    for doc in documents:
        filename = doc[0]
        file_data = doc[1]

        # Extract text from the PDF using PyMuPDF (fitz)
        doc_text = self.extract_text_from_pdf(file_data)

        # Optionally, split text if needed
        splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        chunks = splitter.split_text(doc_text)

        # Convert text to markdown
        markdown_text = md(doc_text)

        markdown_documents.append({
            'filename': filename,
            'markdown': markdown_text,
            'text_chunks': chunks  # if you want to keep the text chunks for further use
        })

    return markdown_documents

def extract_text_from_pdf(self, file_data: bytes) -> str:
    """Extract text from PDF using PyMuPDF."""
    pdf_document = fitz.open(stream=file_data, filetype="pdf")
    text = ""
    for page_num in range(pdf_document.page_count):
        page = pdf_document.load_page(page_num)
        text += page.get_text()
    return text


embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/multi-qa-mpnet-base-dot-v1")




class VectorStoreRetrainer:
    async def retrain_vectorstore(self):
        engine = connect_via_public_ip()
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)
        db = SessionLocal()

        documents = await get_all_documents(db)
        db.close()
        
        embeddings_list = embedding_model.embed_documents(documents.texts)
        embeddings = [np.array(e).tolist() for e in embeddings_list]

        # 3. Utwórz engine i użyj go w kontekście transakcji
        engine = connect_via_public_ip()
        with engine.begin() as connection:
            insert_query = """
                INSERT INTO embeddings (text, embedding)
                VALUES (:text, :embedding)
            """

            data_to_insert = [
                {"text": txt, "embedding": emb}
                for txt, emb in zip(documents.texts, embeddings)
            ]

            for record in data_to_insert:
                connection.execute(text(insert_query), record)

        
        return documents
import numpy as np
import sqlalchemy
from sqlalchemy import text
import psycopg2  # Driver do PostgreSQL
from fastapi import APIRouter
from pydantic import BaseModel
from langchain.embeddings import HuggingFaceEmbeddings

router = APIRouter(prefix="/upload_vector", tags=["upload_vector"])

# Model danych przyjmowanych przez endpoint
class Documents(BaseModel):
    texts: list[str]

def connect_via_public_ip() -> sqlalchemy.engine.base.Engine:
    """
    Łączy się z bazą PostgreSQL w Cloud SQL przez publiczny IP, używając standardowego
    connection stringa (psycopg2).
    """
    # Zmień te wartości na odpowiednie dla Twojej instancji:
    host = "35.246.200.139"  # publiczny IP z Cloud SQL
    port = 5432              # port PostgreSQL
    db_user = "postgres"     # nazwa użytkownika w PostgreSQL
    db_pass = '()+;Cf#V?+`?jqp"'  # hasło do bazy
    db_name = "postgres"     # nazwa bazy

    # Tworzymy poprawny connection string dla SQLAlchemy:
    connection_url = f"postgresql+psycopg2://{db_user}:{db_pass}@{host}:{port}/{db_name}"

    # Inicjalizujemy Engine SQLAlchemy:
    engine = sqlalchemy.create_engine(connection_url)
    return engine

@router.post("/")
async def upload_documents(documents: Documents):
    """
    Endpoint FastAPI przyjmujący listę tekstów, generujący embeddingi
    i zapisujący je w tabeli 'embeddings' w bazie PostgreSQL.
    """
    # 1. Wygeneruj embeddingi za pomocą HuggingFaceEmbeddings
    embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/multi-qa-mpnet-base-dot-v1")
    embeddings_list = embedding_model.embed_documents(documents.texts)

    # 2. Konwersja embeddingów na listy float (np. do JSON lub tablicy)
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

    return {"message": "Documents uploaded and embeddings saved successfully."}

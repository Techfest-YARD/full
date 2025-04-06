import os
from fastapi import APIRouter
from pydantic import BaseModel
from langchain.embeddings import HuggingFaceEmbeddings
import sqlalchemy
from google.cloud.sql.connector import Connector, IPTypes
import pymysql
import numpy as np
import time

from services.logger_service import LoggerService

router = APIRouter(prefix="/vectorstore", tags=["upload"])
logger_service = LoggerService()



class Documents(BaseModel):
    texts: list[str]

def connect_with_connector() -> sqlalchemy.engine.base.Engine:
    """
    Initializes a connection pool for a Cloud SQL instance of MySQL.
    """
    instance_connection_name = os.environ["INSTANCE_CONNECTION_NAME"]
    db_user = os.environ["DB_USER"]
    db_pass = os.environ["DB_PASS"]
    db_name = os.environ["DB_NAME"]

    ip_type = IPTypes.PRIVATE if os.environ.get("PRIVATE_IP") else IPTypes.PUBLIC

    # initialize Cloud SQL Python Connector object
    connector = Connector(ip_type=ip_type, refresh_strategy="LAZY")

    def getconn() -> pymysql.connections.Connection:
        conn: pymysql.connections.Connection = connector.connect(
            instance_connection_name,
            "pymysql",
            user=db_user,
            password=db_pass,
            db=db_name,
        )
        return conn

    # SQLAlchemy connection pool for Cloud SQL
    pool = sqlalchemy.create_engine(
        "mysql+pymysql://",
        creator=getconn,
    )
    return pool

@router.post("/upload_documents")
async def upload_documents(documents: Documents):
    start = time.time()
    try:
        # Embedding i zapis
        embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        embeddings = [embedding_model.encode(doc) for doc in documents.texts]
        embeddings = [np.array(e).tolist() for e in embeddings] 

        engine = connect_with_connector()
        with engine.connect() as connection:
            insert_query = """
                INSERT INTO embeddings (text, embedding) 
                VALUES (%s, %s)
            """
            data_to_insert = [(text, embedding) for text, embedding in zip(documents.texts, embeddings)]
            connection.execute(insert_query, data_to_insert)

        duration = int((time.time() - start) * 1000)
        logger_service.log_app_event({
            "event_type": "document_upload",
            "path": "/upload_documents",
            "message": f"{len(documents.texts)} dokumentów zapisanych",
            "status": "success",
            "duration_ms": duration,
            "extra": {"text_count": len(documents.texts)}
        })

        return {"message": "Documents uploaded and embeddings saved successfully."}
    
    except Exception as e:
        logger_service.log_app_event({
            "event_type": "document_upload",
            "path": "/upload_documents",
            "message": "Błąd podczas zapisu dokumentów",
            "status": "error",
            "extra": {"error": str(e)}
        })
        raise


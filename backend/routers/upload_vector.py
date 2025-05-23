import os
from fastapi import APIRouter
from pydantic import BaseModel
from langchain.embeddings import HuggingFaceEmbeddings
import sqlalchemy
from google.cloud.sql.connector import Connector, IPTypes
import pymysql
import numpy as np

router = APIRouter(prefix="/upload_vector", tags=["upload_vector"])

class Documents(BaseModel):
    texts: list[str]

def connect_with_connector() -> sqlalchemy.engine.base.Engine:
    instance_connection_name = "35.246.200.139"
    db_user = "postgres"
    db_pass = "test"
    db_name = "vectorstore"

    ip_type = IPTypes.PRIVATE if os.environ.get("PRIVATE_IP") else IPTypes.PUBLIC
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
    pool = sqlalchemy.create_engine(
        "mysql+pymysql://",
        creator=getconn,
    )
    return pool

@router.post("/")
async def upload_documents(documents: Documents):
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

    return {"message": "Documents uploaded and embeddings saved successfully."}
from fastapi import FastAPI
from routers import chat, upload, test
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
from connectors.DbConnector import router
import uvicorn

load_dotenv()

# import google.cloud.logging
# import logging

# # Inicjalizacja klienta Google Cloud Logging
# client = google.cloud.logging.Client()
# client.setup_logging()

# # Logger aplikacji
# logger = logging.getLogger(__name__)
# logger.setLevel(logging.INFO)
FRONTEND_URL = os.getenv("FRONTEND_URL")

app = FastAPI()
app.include_router(chat.router)
app.include_router(upload.router)
app.include_router(test.router)
app.include_router(router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=8080, reload=True)


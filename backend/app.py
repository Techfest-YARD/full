from fastapi import FastAPI
from routers import chat, upload
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


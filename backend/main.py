from fastapi import FastAPI
from routers import chat, upload

import google.cloud.logging
import logging

# Inicjalizacja klienta Google Cloud Logging
client = google.cloud.logging.Client()
client.setup_logging()

# Logger aplikacji
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

app = FastAPI()
app.include_router(chat.router)
app.include_router(upload.router)

from fastapi import FastAPI

from routers import chat, upload

app = FastAPI()

app.include_router([chat.router, upload.router])
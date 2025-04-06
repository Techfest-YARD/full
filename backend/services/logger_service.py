import psycopg2
from psycopg2 import sql
from datetime import datetime
import os
from dotenv import load_dotenv

# Wczytaj dane z .env
load_dotenv()

DB_PARAMS = {
    "host": os.getenv("POSTGRES_HOST"),
    "port": os.getenv("POSTGRES_PORT"),
    "dbname": os.getenv("POSTGRES_DB_LLM_LOGS"),
    "user": os.getenv("POSTGRES_USER"),
    "password": os.getenv("POSTGRES_PASSWORD"),
}



class LoggerService:
    def __init__(self):
        self.value = os.getenv("DEV", default=True)
        print(self.value)
        if self.value == None:
            self.conn = psycopg2.connect(**DB_PARAMS)
            self.cursor = self.conn.cursor()

    def log_llm_call(self, data: dict):
        if self.value == None:
            self.cursor.execute(
                """
                INSERT INTO llm_logs (query, prompt, response_length, context_length, duration_ms, source, error)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    data.get("query"),
                    data.get("prompt"),
                    data.get("response_length"),
                    data.get("context_length"),
                    data.get("duration_ms"),
                    data.get("source"),
                    data.get("error")
                )
            )
            self.conn.commit()

    def log_app_event(self, data: dict):
        if self.value == None:
            self.cursor.execute(
                """
                INSERT INTO app_logs (event_type, user_id, path, message, status, duration_ms, extra)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    data.get("event_type"),
                    data.get("user_id"),
                    data.get("path"),
                    data.get("message"),
                    data.get("status"),
                    data.get("duration_ms"),
                    json.dumps(data.get("extra")) if data.get("extra") else None
                )   
            )
            self.conn.commit()

    def close(self):
        if self.value == None:
            self.cursor.close()
            self.conn.close()
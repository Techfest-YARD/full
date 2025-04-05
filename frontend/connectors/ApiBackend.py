import requests
import os
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

class ApiBackend:
    def __init__(self):
        self._base_url = os.getenv("BACKEND_URL")
        logger.info(f"BACKEND_URL loaded: {self._base_url} ----")


    def ask_chat(self, message: str) -> str:
        params = {"prompt": message}
        url = f"{self._base_url}/chat"
        logger.info(f"Sending GET request to {url} with params: {params}")
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            logger.info(f"Response: {response.status_code} - {response.text}")
            return response.json().get("response", "[No response]")
        except Exception as e:
            logger.error(f"GET request failed: {e}")
            logger.debug(response.text if 'response' in locals() else "No response object")
            return "[Error during request]"

    def upload_files(self, files: list) -> dict:
        prepared_files = [
            ("files", (file.name, file.read(), "application/pdf"))
            for file in files
        ]
        response = requests.post(f"{self._base_url}/upload", files=prepared_files)
        response.raise_for_status()
        return response.json()
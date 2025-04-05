import requests
import os
from dotenv import load_dotenv

load_dotenv()

class ApiBackend:
    def __init__(self):
        self._base_url = os.getenv("BACKEND_URL")

    def ask_chat(self, message: str) -> str:
        params = {"prompt": message}
        response = requests.get(self._base_url + "/chat", params=params)
        return response.json().get("response", "[No response]")

    def upload_files(self, files: list) -> dict:
        prepared_files = [
            ("files", (file.name, file.read(), "application/pdf"))
            for file in files
        ]
        response = requests.post(f"{self._base_url}/upload", files=prepared_files)
        response.raise_for_status()
        return response.json()
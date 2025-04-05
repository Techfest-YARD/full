import requests

class ApiBackend:
    def __init__(self):
        self._base_url = "http://localhost:8000"

    def ask_chat(self, message, session_id) -> str:
        payload = {"message": message, "session_id": session_id}
        response = requests.post(self._base_url + "/chat", json=payload)
        return response.json().get("response", "[No response]")
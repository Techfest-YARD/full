from dotenv import load_dotenv
import os
import google.generativeai as genai

load_dotenv()

class GeminiService:
    def __init__(self, model_name: str = "gemini-1.5-flash"):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("Brakuje zmiennej środowiskowej GEMINI_API_KEY")

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)

    def ask(self, prompt: str) -> str:
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error: {e}"
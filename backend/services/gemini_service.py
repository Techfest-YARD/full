from dotenv import load_dotenv
import os
import google.generativeai as genai
from concurrent.futures import ThreadPoolExecutor
import asyncio
# import logging
import time

load_dotenv()
# logger = logging.getLogger(__name__)

class GeminiService:
    def __init__(self, model_name: str = "gemini-1.5-flash"):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("Brakuje zmiennej środowiskowej GEMINI_API_KEY")

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)
        self.executor = ThreadPoolExecutor(max_workers=1)

    async def ask(self, prompt: str, timeout: float = 10.0) -> str:
        loop = asyncio.get_event_loop()
        start = time.time()

        # logger.info(f"🔍 Sending prompt to Gemini: {prompt}")

        try:
            result = await asyncio.wait_for(
                loop.run_in_executor(self.executor, self.model.generate_content, prompt),
                timeout=timeout
            )
            duration = time.time() - start
            # logger.info(f"✅ Gemini responded in {duration:.2f}s")
            return result.text

        except asyncio.TimeoutError:
            # logger.error("❌ Gemini request timed out")
            return "Error: Request timed out"

        except Exception as e:
            # logger.exception("❌ Gemini error occurred")
            return f"Error: {e}"

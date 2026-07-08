import os
from abc import ABC
from google import genai
from dotenv import load_dotenv

load_dotenv()

class BaseAgent(ABC):
    def __init__(self, model: str):
        # Initializes Gemini Client using GEMINI_API_KEY from environment
        self.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        self.model = model

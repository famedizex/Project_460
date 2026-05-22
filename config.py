# config.py
import os

from dotenv import load_dotenv
load_dotenv()
API_KEY = os.environ.get("GROQ_API_KEY", "")
PORT = int(os.environ.get("PORT", 8000))
HOST = "0.0.0.0"

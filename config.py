# config.py
import os

API_KEY = os.environ.get("GROQ_API_KEY", "")
PORT = int(os.environ.get("PORT", 8000))
HOST = "0.0.0.0"

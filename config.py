# config.py
import os

API_KEY = os.environ.get("GROQ_API_KEY", "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")
PORT = int(os.environ.get("PORT", 8000))
HOST = "0.0.0.0"

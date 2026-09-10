import os

from dotenv import load_dotenv

load_dotenv()

CEREBRAS_API_KEY = os.getenv("CEREBRAS_API_KEY", "").strip()
CEREBRAS_BASE_URL = os.getenv("CEREBRAS_BASE_URL", "https://api.cerebras.ai/v1").rstrip("/")
CEREBRAS_MODEL = os.getenv("CEREBRAS_MODEL", "qwen-3.8-27b")

MAX_LOG_DAYS = 60
MAX_LOG_CHARS = 2000
MAX_UPLOAD_BYTES = 1_000_000

WELLBEING_LABELS = {
    0: "Very well",
    1: "Slightly below par",
    2: "Poor",
    3: "Very poor",
    4: "Terrible",
}

PAIN_LABELS = {
    0: "None",
    1: "Mild",
    2: "Moderate",
    3: "Severe",
}

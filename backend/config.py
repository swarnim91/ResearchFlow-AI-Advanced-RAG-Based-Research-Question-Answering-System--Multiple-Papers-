import os
from dotenv import load_dotenv

# Disable Chroma telemetry to eliminate noisy warnings and improve speed
os.environ["ANONYMIZED_TELEMETRY"] = "False"

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, ".."))

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

PAPERS_DIR = os.getenv("PAPERS_DIR", os.path.join(PROJECT_ROOT, "papers"))
VECTOR_DB_DIR = os.getenv("VECTOR_DB_DIR", os.path.join(PROJECT_ROOT, "vector_db"))
METADATA_DIR = os.getenv("METADATA_DIR", os.path.join(PROJECT_ROOT, "metadata"))

CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))
NUM_RETRIEVED_DOCS = int(os.getenv("NUM_RETRIEVED_DOCS", "4"))
TEMPERATURE = float(os.getenv("TEMPERATURE", "0"))
MODEL_NAME = os.getenv("MODEL_NAME", "openai/gpt-oss-20b")
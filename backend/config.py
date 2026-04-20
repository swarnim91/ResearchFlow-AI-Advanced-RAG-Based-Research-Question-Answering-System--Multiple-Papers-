import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
PAPERS_DIR = os.getenv("PAPERS_DIR", "papers")
VECTOR_DB_DIR = os.getenv("VECTOR_DB_DIR", "vector_db")
METADATA_DIR = os.getenv("METADATA_DIR", "metadata")
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "500"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "100"))
NUM_RETRIEVED_DOCS = int(os.getenv("NUM_RETRIEVED_DOCS", "4"))
TEMPERATURE = float(os.getenv("TEMPERATURE", "0"))
MODEL_NAME = os.getenv("MODEL_NAME", "llama-3.3-70b-versatile")
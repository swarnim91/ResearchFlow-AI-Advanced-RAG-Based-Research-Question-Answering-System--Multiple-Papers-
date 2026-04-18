import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
PAPERS_DIR = "papers"
VECTOR_DB_DIR = "vector_db"
METADATA_DIR = "metadata"
CHUNK_SIZE = 500
CHUNK_OVERLAP = 100
NUM_RETRIEVED_DOCS = 4  
TEMPERATURE = 0
MODEL_NAME = "llama-3.3-70b-versatile"
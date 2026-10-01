import os
import sys
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pypdf import PdfReader
from pydantic import BaseModel, Field
from langchain_groq import ChatGroq
from config import METADATA_DIR, GROQ_API_KEY, MODEL_NAME

class DocumentMetadata(BaseModel):
    title: str = Field(description="The title of the academic paper.")
    authors: str = Field(description="The authors of the paper. Use comma-separated names.")
    year: str = Field(description="The publication year of the paper. If unknown, use 'Unknown'.")
    summary: str = Field(description="A 1-2 sentence brief summary of the paper.")
    keywords: str = Field(description="Comma-separated keywords related to the paper.")

def extract_metadata(pdf_path):
    """Extract metadata from PDF using an LLM."""
    filename = os.path.basename(pdf_path)
    try:
        reader = PdfReader(pdf_path)
        
        # Extract first 3 pages (or fewer) to get solid context
        num_pages = min(3, len(reader.pages))
        text_content = ""
        for i in range(num_pages):
            extracted = reader.pages[i].extract_text()
            if extracted:
                text_content += extracted + "\n"
            
        if not text_content.strip():
            text_content = f"Filename: {filename}. Content could not be extracted."

        llm = ChatGroq(
            groq_api_key=GROQ_API_KEY,
            model_name=MODEL_NAME,
            temperature=0,
            request_timeout=60,
            max_retries=3,
        )
        
        structured_llm = llm.with_structured_output(DocumentMetadata)
        
        prompt = f"Please extract the metadata for the following academic paper snippet:\n\n{text_content[:4000]}"
        
        result = structured_llm.invoke(prompt)
        
        # Safely handle dictionary or Pydantic model response
        def _get_val(key, default):
            if isinstance(result, dict):
                return result.get(key, default)
            return getattr(result, key, default)

        return {
            'title': _get_val('title', os.path.splitext(filename)[0]),
            'authors': _get_val('authors', 'Unknown'),
            'year': str(_get_val('year', 'Unknown')),
            'summary': _get_val('summary', ''),
            'keywords': _get_val('keywords', ''),
            'filename': filename
        }
    except Exception as e:
        print(f"Error extracting metadata with LLM for {filename}: {e}")
        # Fallback: try to extract title from filename
        title = os.path.splitext(filename)[0].replace('_', ' ').replace('-', ' ').title()
        return {
            'title': title,
            'authors': 'Unknown',
            'year': 'Unknown',
            'summary': 'Metadata extraction timed out or failed.',
            'keywords': '',
            'filename': filename
        }

def save_metadata(filename, metadata):
    """Save metadata to JSON file."""
    os.makedirs(METADATA_DIR, exist_ok=True)
    json_path = os.path.join(METADATA_DIR, f"{os.path.splitext(filename)[0]}.json")
    with open(json_path, 'w') as f:
        json.dump(metadata, f, indent=2)
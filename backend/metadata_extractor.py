import os
import json
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
            text_content += reader.pages[i].extract_text() + "\n"
            
        if not text_content.strip():
            text_content = f"Filename: {filename}. Content could not be extracted."

        llm = ChatGroq(
            groq_api_key=GROQ_API_KEY,
            model_name=MODEL_NAME,
            temperature=0
        )
        
        structured_llm = llm.with_structured_output(DocumentMetadata)
        
        prompt = f"Please extract the metadata for the following academic paper snippet:\n\n{text_content[:4000]}"
        
        result = structured_llm.invoke(prompt)
        
        return {
            'title': result.title,
            'authors': result.authors,
            'year': result.year,
            'summary': result.summary,
            'keywords': result.keywords,
            'filename': filename
        }
    except Exception as e:
        print(f"Error extracting metadata with LLM for {filename}: {e}")
        return {
            'title': filename,
            'authors': 'Unknown',
            'year': 'Unknown',
            'summary': 'Extraction failed.',
            'keywords': '',
            'filename': filename
        }

def save_metadata(filename, metadata):
    """Save metadata to JSON file."""
    os.makedirs(METADATA_DIR, exist_ok=True)
    json_path = os.path.join(METADATA_DIR, f"{os.path.splitext(filename)[0]}.json")
    with open(json_path, 'w') as f:
        json.dump(metadata, f, indent=2)
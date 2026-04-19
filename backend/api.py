import os
import sys
import shutil
import uuid

# Add parent directory to path so we can import main, config, etc.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

from main import (
    create_vector_store,
    load_vector_store,
    create_synthesis_chain,
    ask_question,
    load_paper_with_metadata,
)
from config import PAPERS_DIR, VECTOR_DB_DIR, METADATA_DIR

app = FastAPI(title="ResearchFlow AI API")

# CORS — allow the React dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# In-memory state
# ---------------------------------------------------------------------------
_qa_chain = None


def _get_qa_chain(force_reload: bool = False):
    """Lazy-load the QA chain."""
    global _qa_chain
    if _qa_chain is None or force_reload:
        vs = load_vector_store()
        if vs is None:
            return None
        _qa_chain = create_synthesis_chain(vs)
    return _qa_chain


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------
class QuestionRequest(BaseModel):
    question: str


class PaperInfo(BaseModel):
    title: str
    authors: str
    year: str


class AskResponse(BaseModel):
    answer: str
    cited_papers: dict


class StatusResponse(BaseModel):
    indexed: bool
    paper_count: int
    papers: List[str]


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.get("/api/status", response_model=StatusResponse)
def get_status():
    """Return whether papers are indexed and list them."""
    papers: List[str] = []
    if os.path.exists(PAPERS_DIR):
        papers = [f for f in os.listdir(PAPERS_DIR) if f.lower().endswith(".pdf")]

    vs = load_vector_store()
    return StatusResponse(
        indexed=vs is not None,
        paper_count=len(papers),
        papers=papers,
    )


@app.post("/api/upload")
async def upload_papers(files: List[UploadFile] = File(...)):
    """Upload PDFs, index them into ChromaDB."""
    global _qa_chain
    
    _qa_chain = None
    import gc
    gc.collect()

    os.makedirs(PAPERS_DIR, exist_ok=True)

    # Clean old data
    for d in [VECTOR_DB_DIR, METADATA_DIR]:
        if os.path.exists(d):
            shutil.rmtree(d, ignore_errors=True)
        os.makedirs(d, exist_ok=True)

    # Clean papers not in the current upload set
    current_filenames = {f.filename for f in files}
    if os.path.exists(PAPERS_DIR):
        for existing in os.listdir(PAPERS_DIR):
            if existing not in current_filenames:
                try:
                    os.remove(os.path.join(PAPERS_DIR, existing))
                except Exception:
                    pass

    # Save uploaded files
    file_paths = []
    for f in files:
        path = os.path.join(PAPERS_DIR, f.filename)
        with open(path, "wb") as dst:
            content = await f.read()
            dst.write(content)
        file_paths.append(path)

    # Index papers
    vectorstore = None
    successful_count = 0
    for file_path in file_paths:
        try:
            docs = load_paper_with_metadata(file_path, "uploaded")
            if not docs:
                continue
            if vectorstore is None:
                vectorstore = create_vector_store(docs)
                successful_count += 1
            else:
                from langchain_text_splitters import RecursiveCharacterTextSplitter

                text_splitter = RecursiveCharacterTextSplitter(
                    chunk_size=500, chunk_overlap=100
                )
                chunks = text_splitter.split_documents(docs)
                if chunks:
                    ids = [str(uuid.uuid4()) for _ in range(len(chunks))]
                    vectorstore.add_documents(chunks, ids=ids)
                    vectorstore.persist()
                successful_count += 1
        except Exception as e:
            print(f"Failed to process {file_path}: {e}")

    if successful_count == 0:
        raise HTTPException(status_code=400, detail="Failed to parse any of the provided documents.")

    # Reload QA chain
    _qa_chain = None
    _get_qa_chain(force_reload=True)

    return {"message": "Papers indexed successfully", "count": successful_count}


@app.post("/api/ask", response_model=AskResponse)
def ask(req: QuestionRequest):
    """Ask a research question."""
    if not req.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    chain = _get_qa_chain()
    if chain is None:
        raise HTTPException(
            status_code=400,
            detail="No papers indexed yet. Upload and process papers first.",
        )

    result = ask_question(chain, req.question)
    return AskResponse(
        answer=result["answer"],
        cited_papers=result["cited_papers"],
    )

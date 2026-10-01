import os
import sys
import shutil
import uuid
import traceback

# Ensure the backend directory is in sys.path so imports work regardless of working directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from typing import List
from fastapi import FastAPI, UploadFile, File, HTTPException, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from main import (
    create_vector_store,
    load_vector_store,
    create_synthesis_chain,
    ask_question,
    load_paper_with_metadata,
)
from config import PAPERS_DIR, VECTOR_DB_DIR, METADATA_DIR, CHUNK_SIZE, CHUNK_OVERLAP

app = FastAPI(title="ResearchFlow AI API")

# CORS — allow React dev server and remote hosts
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=86400,
)


# ---------------------------------------------------------------------------
# Global exception handler — ensures all errors return valid JSON
# ---------------------------------------------------------------------------
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Catch-all handler to prevent raw HTML error pages and ensure JSON responses."""
    print(f"Unhandled exception: {exc}")
    traceback.print_exc()
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error: {str(exc)}"},
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
# API Routes
# ---------------------------------------------------------------------------
@app.get("/")
@app.head("/")
@app.get("/api")
@app.head("/api")
@app.get("/api/health")
@app.head("/api/health")
def health_check():
    """Simple health check for connectivity testing."""
    return {"status": "ok", "message": "ResearchFlow Backend is up and running!"}


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


def process_papers_background(file_paths: List[str]):
    """Background task to heavily process PDFs and create embeddings."""
    global _qa_chain
    import gc
    
    print(f"[BG] Starting background processing for {len(file_paths)} file(s)...")
    vectorstore = None
    successful_count = 0
    errors = []
    
    for file_path in file_paths:
        try:
            print(f"[BG] Processing: {os.path.basename(file_path)}")
            docs = load_paper_with_metadata(file_path, "uploaded")
            if not docs:
                errors.append(f"{os.path.basename(file_path)}: No content extracted")
                print(f"[BG] WARNING: No content extracted from {os.path.basename(file_path)}")
                continue
            print(f"[BG] Extracted {len(docs)} page(s), creating embeddings...")
            if vectorstore is None:
                vectorstore = create_vector_store(docs)
                successful_count += 1
            else:
                from langchain_text_splitters import RecursiveCharacterTextSplitter
                text_splitter = RecursiveCharacterTextSplitter(
                    chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP
                )
                chunks = text_splitter.split_documents(docs)
                if chunks:
                    ids = [str(uuid.uuid4()) for _ in range(len(chunks))]
                    vectorstore.add_documents(chunks, ids=ids)
                    try:
                        vectorstore.persist()
                    except Exception:
                        pass
                successful_count += 1
            print(f"[BG] ✓ Successfully indexed {os.path.basename(file_path)}")
        except Exception as e:
            errors.append(f"{os.path.basename(file_path)}: {str(e)}")
            print(f"[BG] ✗ Failed to process {file_path}: {e}")
            traceback.print_exc()
            
    print(f"[BG] Processing complete: {successful_count} succeeded, {len(errors)} failed")
    if errors:
        print(f"[BG] Errors: {errors}")
    
    # Always reload QA chain after processing
    _qa_chain = None
    _get_qa_chain(force_reload=True)
    gc.collect()


@app.post("/api/upload")
async def upload_papers(background_tasks: BackgroundTasks, files: List[UploadFile] = File(...)):
    """Upload PDFs, and queue them for indexing into ChromaDB."""
    os.makedirs(PAPERS_DIR, exist_ok=True)

    # Clean old vector/metadata directories
    for d in [VECTOR_DB_DIR, METADATA_DIR]:
        if os.path.exists(d):
            try:
                shutil.rmtree(d, ignore_errors=True)
            except Exception as e:
                print(f"Warning cleaning directory {d}: {e}")
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

    # Save uploaded files quickly
    file_paths = []
    for f in files:
        path = os.path.join(PAPERS_DIR, f.filename)
        with open(path, "wb") as dst:
            content = await f.read()
            dst.write(content)
        file_paths.append(path)

    # Hand off heavy processing to background
    background_tasks.add_task(process_papers_background, file_paths)

    return {
        "message": "Files uploaded successfully. Processing started in the background.",
        "count": len(files),
        "background": True
    }


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


# ---------------------------------------------------------------------------
# Serve Frontend Static Files (if frontend/dist exists)
# Allows full-stack deployment on a single port/service
# ---------------------------------------------------------------------------
DIST_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend", "dist"))

if os.path.exists(DIST_DIR):
    app.mount("/assets", StaticFiles(directory=os.path.join(DIST_DIR, "assets")), name="static_assets")

    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        # Serve index.html for all non-api routes
        if full_path.startswith("api"):
            raise HTTPException(status_code=404, detail="API endpoint not found")
        file_path = os.path.join(DIST_DIR, full_path)
        if os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(DIST_DIR, "index.html"))

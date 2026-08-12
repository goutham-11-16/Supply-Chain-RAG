"""
api/main.py — Supply Chain RAG FastAPI Backend (Bonus)
Provides REST API endpoints for ingestion, querying, and stats.
Run with: uvicorn api.main:app --reload
Docs at: http://localhost:8000/docs
"""

import os
import sys
import tempfile
from typing import List, Optional

from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel

# Add parent directory to path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ingest import ingest_files, get_collection_stats
from rag import ask as rag_ask

# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------
app = FastAPI(
    title="Supply Chain RAG API",
    description="REST API for the Supply Chain RAG System — Upload PDFs, ask questions about supply chain performance and procurement policies.",
    version="1.0.0",
)

# ---------------------------------------------------------------------------
# Response models
# ---------------------------------------------------------------------------
class IngestResponse(BaseModel):
    files: int
    chunks: int

class SourceItem(BaseModel):
    file: str
    page: object  # int or str

class AskRequest(BaseModel):
    question: str
    top_k: Optional[int] = 6

class AskResponse(BaseModel):
    answer: str
    sources: List[SourceItem]

class StatsResponse(BaseModel):
    collection_name: str
    total_chunks: int
    embedding_model: str
    llm_model: str

# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.post("/ingest", response_model=IngestResponse)
async def ingest_endpoint(files: List[UploadFile] = File(...)):
    """
    Upload one or more PDF files for ingestion.
    Both documents are indexed into the same collection for cross-document queries.
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")

    temp_paths = []
    try:
        tmp_dir = tempfile.mkdtemp()
        for f in files:
            if not f.filename.lower().endswith(".pdf"):
                raise HTTPException(
                    status_code=400,
                    detail=f"Only PDF files are accepted. Got: {f.filename}"
                )
            path = os.path.join(tmp_dir, f.filename)
            content = await f.read()
            with open(path, "wb") as out:
                out.write(content)
            temp_paths.append(path)

        n_files, n_chunks = ingest_files(temp_paths)
        return IngestResponse(files=n_files, chunks=n_chunks)

    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        import shutil
        if temp_paths:
            shutil.rmtree(os.path.dirname(temp_paths[0]), ignore_errors=True)


@app.post("/ask", response_model=AskResponse)
async def ask_endpoint(request: AskRequest):
    """
    Ask a question about the indexed supply chain documents.
    Returns the answer and source citations from both documents.
    """
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    try:
        result = rag_ask(request.question, top_k=request.top_k)
        sources = [SourceItem(file=s["file"], page=s["page"]) for s in result["sources"]]
        return AskResponse(answer=result["answer"], sources=sources)

    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stats", response_model=StatsResponse)
async def stats_endpoint():
    """
    Get stats about the current ChromaDB collection.
    Returns collection name, total chunks, embedding model, and LLM model.
    """
    stats = get_collection_stats()
    if "error" in stats:
        raise HTTPException(status_code=500, detail=stats["error"])

    return StatsResponse(
        collection_name=stats["collection_name"],
        total_chunks=stats["total_chunks"],
        embedding_model=stats["embedding_model"],
        llm_model=stats["llm_model"],
    )


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "service": "Supply Chain RAG API",
        "status": "running",
        "docs": "/docs",
    }

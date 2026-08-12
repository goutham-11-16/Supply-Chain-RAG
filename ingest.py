"""
ingest.py — Supply Chain RAG Ingestion Pipeline
Loads PDF files, chunks them, embeds with OpenAI or OpenAI-compatible models, and stores in ChromaDB.
Uses larger chunks (1200) to keep tables and scorecards intact.
Prefixes chunks with document title to disambiguate Review vs Handbook.
"""

import os
import sys
import shutil
import ssl
import httpx
from typing import List, Tuple, Any

# Fix SSL verification issue on Windows
ssl._create_default_https_context = ssl._create_unverified_context

from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
except ImportError:
    from langchain.text_splitter import RecursiveCharacterTextSplitter

from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from fallback_utils import DeterministicLocalEmbeddings

# ---------------------------------------------------------------------------
# Load environment
# ---------------------------------------------------------------------------
load_dotenv()

# ---------------------------------------------------------------------------
# Configuration — tuned for supply chain documents with tables
# ---------------------------------------------------------------------------
CHROMA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chroma_db")
COLLECTION_NAME = "supplychain_rag"
CHUNK_SIZE = 1200          # larger to keep scorecards and policy tables intact
CHUNK_OVERLAP = 150        # preferred overlap to preserve table context across boundaries
EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")

# The two provided PDFs (relative to project root's parent)
PROVIDED_PDFS = [
    "Meridian_Supply_Chain_Review_Q1_FY2025-26.pdf",
    "Meridian_Procurement_Policy_Handbook_v4.2.pdf",
]


def get_embeddings() -> Any:
    """
    Return OpenAI embeddings if a valid key/endpoint is available.
    Falls back gracefully to DeterministicLocalEmbeddings if API key is invalid/missing.
    """
    api_key = os.getenv("OPENAI_API_KEY", "")
    base_url = os.getenv("OPENAI_BASE_URL") or os.getenv("OPENAI_API_BASE")
    
    if not api_key or api_key == "your_key_here" or api_key == "antigravity-local":
        if not base_url:
            return DeterministicLocalEmbeddings()

    try:
        custom_http_client = httpx.Client(verify=False, follow_redirects=True)
        kwargs = {
            "model": EMBEDDING_MODEL,
            "openai_api_key": api_key if api_key else "placeholder",
            "check_embedding_ctx_length": False,
            "http_client": custom_http_client,
        }
        if base_url:
            kwargs["openai_api_base"] = base_url

        embeddings = OpenAIEmbeddings(**kwargs)
        embeddings.embed_query("test")
        return embeddings
    except Exception as e:
        print(f"[NOTE] Using local deterministic embeddings fallback (Reason: {e})")
        return DeterministicLocalEmbeddings()


def auto_copy_provided_pdfs():
    """
    Copy the two provided Meridian PDFs from the parent assignment directory
    into the local data/ folder if they aren't already there.
    """
    project_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(project_dir, "data")
    parent_dir = os.path.dirname(project_dir)

    os.makedirs(data_dir, exist_ok=True)

    copied = 0
    for pdf_name in PROVIDED_PDFS:
        src = os.path.join(parent_dir, pdf_name)
        dst = os.path.join(data_dir, pdf_name)
        if os.path.exists(src) and not os.path.exists(dst):
            shutil.copy2(src, dst)
            print(f"  [+] Copied {pdf_name} to data/")
            copied += 1
    
    if copied > 0:
        print(f"  [+] {copied} PDFs copied to data/ folder")
    return data_dir


def load_pdfs(file_paths: List[str]) -> list:
    """Load one or more PDFs and return a flat list of LangChain Document objects with metadata."""
    all_docs = []
    for path in file_paths:
        if not os.path.exists(path):
            print(f"[WARN] File not found, skipping: {path}")
            continue
        loader = PyPDFLoader(path)
        docs = loader.load()
        filename = os.path.basename(path)
        doc_type = "review" if "Review" in filename else "policy"
        for i, doc in enumerate(docs):
            page_num = i + 1
            doc.metadata["source"] = filename
            doc.metadata["source_file"] = filename
            doc.metadata["page"] = page_num
            doc.metadata["document_type"] = doc_type
        all_docs.extend(docs)
        print(f"  [+] Loaded {filename} ({doc_type}) -- {len(docs)} pages")
    return all_docs


def chunk_documents(documents: list) -> list:
    """
    Split documents into chunks using recursive character text splitting.
    Prefix each chunk's text with document label to disambiguate performance review vs policy handbook.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = splitter.split_documents(documents)
    
    for chunk in chunks:
        source = chunk.metadata.get("source", chunk.metadata.get("source_file", ""))
        doc_type = chunk.metadata.get("document_type", "")
        page_num = chunk.metadata.get("page", 1)
        doc_title = "Performance Review" if doc_type == "review" else "Procurement Policy Handbook"
        prefix = f"[{doc_title} - {source} - Page {page_num}]\n"
        if not chunk.page_content.startswith("["):
            chunk.page_content = prefix + chunk.page_content

    return chunks


def store_chunks(chunks: list, embeddings: Any) -> Chroma:
    """Embed chunks and persist them in ChromaDB."""
    try:
        # Clear existing collection cleanly using Chroma API (bypasses Windows file locks)
        existing = Chroma(
            collection_name=COLLECTION_NAME,
            persist_directory=CHROMA_DIR,
            embedding_function=embeddings,
        )
        existing.delete_collection()
    except Exception:
        pass

    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        collection_name=COLLECTION_NAME,
        persist_directory=CHROMA_DIR,
    )
    return vectorstore


def load_existing_store(embeddings: Any) -> Chroma:
    """Load an already-persisted ChromaDB store."""
    return Chroma(
        collection_name=COLLECTION_NAME,
        persist_directory=CHROMA_DIR,
        embedding_function=embeddings,
    )


def ingest_files(file_paths: List[str]) -> Tuple[int, int]:
    """
    Full ingestion pipeline: load → chunk → embed → store.
    Returns (number_of_files, number_of_chunks).
    Both PDFs go into the SAME ChromaDB collection (critical for cross-document queries).
    """
    print("\n[+] Loading PDFs...")
    documents = load_pdfs(file_paths)
    if not documents:
        return 0, 0

    print(f"\n[+] Chunking {len(documents)} pages (size={CHUNK_SIZE}, overlap={CHUNK_OVERLAP})...")
    chunks = chunk_documents(documents)
    print(f"    Created {len(chunks)} chunks")

    print("\n[+] Embedding and storing in ChromaDB...")
    embeddings = get_embeddings()
    store_chunks(chunks, embeddings)
    print(f"    Stored {len(chunks)} chunks in {CHROMA_DIR}")

    return len(file_paths), len(chunks)


def get_collection_stats() -> dict:
    """Return stats about the current ChromaDB collection."""
    try:
        embeddings = get_embeddings()
        store = load_existing_store(embeddings)
        collection = store._collection
        count = collection.count()
        return {
            "collection_name": COLLECTION_NAME,
            "total_chunks": count,
            "embedding_model": EMBEDDING_MODEL,
            "llm_model": os.getenv("OPENAI_MODEL_NAME", "gpt-4o"),
            "persist_directory": CHROMA_DIR,
        }
    except Exception as e:
        return {"error": str(e)}


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    data_dir = auto_copy_provided_pdfs()

    if len(sys.argv) >= 2:
        files = sys.argv[1:]
    else:
        files = [
            os.path.join(data_dir, f)
            for f in os.listdir(data_dir)
            if f.endswith(".pdf")
        ]
        if not files:
            print("No PDF files found. Place PDFs in data/ or pass them as arguments.")
            print("Usage: python ingest.py [pdf1] [pdf2] ...")
            sys.exit(1)
        print(f"Found {len(files)} PDFs in data/ folder")

    n_files, n_chunks = ingest_files(files)
    print(f"\n[Done] {n_files} files processed, {n_chunks} chunks stored.")

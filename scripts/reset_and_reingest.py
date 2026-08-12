"""
reset_and_reingest.py — Clean Re-ingestion Script for Meridian Supply Chain RAG
Clears existing ChromaDB vector store and re-indexes the Meridian PDF documents.
"""

import os
import sys

# Change to project root directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
os.chdir(PROJECT_ROOT)

from dotenv import load_dotenv
from ingest import ingest_files, auto_copy_provided_pdfs, get_collection_stats

load_dotenv()

def main():
    print("=========================================================================")
    print("MERIDIAN SUPPLY CHAIN RAG — DATABASE RE-INDEXING UTILITY")
    print("=========================================================================")
    
    data_dir = auto_copy_provided_pdfs()
    pdf_files = [os.path.join(data_dir, f) for f in os.listdir(data_dir) if f.endswith(".pdf")]
    
    if not pdf_files:
        print("❌ Error: No PDF documents found in data/ folder.")
        sys.exit(1)
        
    print(f"[+] Found {len(pdf_files)} PDF documents in data/ directory.")
    n_files, n_chunks = ingest_files(pdf_files)
    
    stats = get_collection_stats()
    print("\n✅ [SUCCESS] Vector store re-indexed successfully!")
    print(f"    - Collection Name: {stats.get('collection_name')}")
    print(f"    - Total Vector Chunks: {stats.get('total_chunks')}")
    print(f"    - Embedding Model: {stats.get('embedding_model')}")
    print(f"    - Persistence Path: {stats.get('persist_directory')}\n")

if __name__ == "__main__":
    main()

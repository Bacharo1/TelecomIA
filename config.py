# config.py
import os
from pathlib import Path
import chromadb
from langchain_ollama import OllamaEmbeddings

# On définit tout ici une seule fois
UPLOAD_DIR = Path("storage/pdfs")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

try:
    CHROMA_CLIENT = chromadb.HttpClient(host="localhost", port=8000)
    EMBEDDINGS = OllamaEmbeddings(model="nomic-embed-text")
    COLLECTION_NAME = "mistral_kb"
except Exception as e:
    chromadb.logger.error(f"Initialization failed: {e}")
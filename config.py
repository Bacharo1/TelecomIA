# config.py
import os
from pathlib import Path
import chromadb
from langchain_ollama import OllamaEmbeddings

from dotenv import load_dotenv

load_dotenv()
os.environ["HF_TOKEN"] = os.getenv("HF_TOKEN")

# Localise le dossier où se trouve config.py
BASE_DIR = Path(__file__).resolve().parent

# Crée le chemin absolu vers storage
UPLOAD_DIR = BASE_DIR / "storage" / "pdfs"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

try:
    CHROMA_CLIENT = chromadb.HttpClient(host="localhost", port=8000)
    EMBEDDINGS = OllamaEmbeddings(model="nomic-embed-text")
    COLLECTION_NAME = "mistral_kb"
except Exception as e:
    chromadb.logger.error(f"Initialization failed: {e}")
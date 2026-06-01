# config.py
import os
from pathlib import Path
import chromadb
from langchain_ollama import OllamaEmbeddings

from dotenv import load_dotenv
from sqlalchemy import create_engine
from passlib.context import CryptContext

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


ingestion_status = {}    



# Configuration de la sécurité
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Configuration de la Base de Données
load_dotenv()

db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")  
db_host = os.getenv("DB_HOST")
db_port = os.getenv("DB_PORT")
db_name = os.getenv("DB_NAME")

database_url = f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
engine = create_engine(database_url)
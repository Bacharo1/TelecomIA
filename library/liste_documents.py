import os


# Imports tiers
from fastapi import APIRouter
from dotenv import load_dotenv

from config import UPLOAD_DIR


load_dotenv()
router = APIRouter()

@router.get("/liste-documents")
async def liste_docs():
    if not os.path.exists(UPLOAD_DIR):
        return {"documents": []}
    # Liste tous les fichiers dans le dossier de stockage
    files = os.listdir(UPLOAD_DIR)
    # On ne garde que les PDF
    pdfs = [f for f in files if f.lower().endswith('.pdf')]
    return {"documents": pdfs}
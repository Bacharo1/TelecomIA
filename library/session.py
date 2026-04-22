# Imports standard
import os

# Imports tiers
from fastapi import APIRouter, Form
from config import CHROMA_CLIENT, COLLECTION_NAME, EMBEDDINGS, UPLOAD_DIR
from dotenv import load_dotenv

# Imports locaux
from config import UPLOAD_DIR

load_dotenv()
router = APIRouter()




@router.post("/clear-session")
async def clear():
    print("Requête de réinitialisation reçue !")
    try:
        # Nettoyage physique
        if os.path.exists(UPLOAD_DIR):
            for filename in os.listdir(UPLOAD_DIR):
                file_path = os.path.join(UPLOAD_DIR, filename)
                try:
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                except Exception as e:
                    print(f"Impossible de supprimer {filename}: {e}")

        # Nettoyage ChromaDB
        collections = CHROMA_CLIENT.list_collections()
        print(f"Collections avant suppression : {[c.name for c in collections]}")
        CHROMA_CLIENT.delete_collection(COLLECTION_NAME)
        CHROMA_CLIENT.create_collection(COLLECTION_NAME)
        print(f"Collections après suppression : {[c.name for c in collections]}")
        
        print("Nettoyage réussi !")
        return {"status": "success", "message": "Base et storage réinitialisés"}
    except Exception as e:
        print(f"Erreur globale clear: {e}")
        return {"status": "error", "message": str(e)}
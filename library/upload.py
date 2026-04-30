# Imports standard
import os

# Imports tiers
from fastapi import APIRouter, Form, UploadFile, File
from config import CHROMA_CLIENT, COLLECTION_NAME, EMBEDDINGS, UPLOAD_DIR
from dotenv import load_dotenv

# Imports locaux
from library.ingest import ingest_file_to_db
from config import UPLOAD_DIR

load_dotenv()
router = APIRouter()



@router.post("/import")
async def import_file(
    file: UploadFile = File(None),
    existing_file: str = Form(None)
):

    # --- 1. Validation ---
    nom_fichier = file.filename if (file and file.filename) else existing_file
    if not nom_fichier:
        return {"reponse": "Erreur : Aucun fichier sélectionné."}

    file_path = os.path.join(UPLOAD_DIR, nom_fichier)

    try:
        # --- 2. Sauvegarde du fichier (si nouvel upload) ---
        if file:
            if not os.path.exists(file_path):
                content = await file.read()
                with open(file_path, "wb") as f:
                    f.write(content)
                print(f" Fichier sauvegardé : {file_path}")
            else:
                print(f" Fichier existe déjà : {file_path}")

        # --- 3. Ingestion dans ChromaDB ---
        ingest_file_to_db(file_path, use_ocr=True)

        # --- 4. Retour ---
        return {
            "reponse": "Document importé et analysé avec succès !",
            "filename": nom_fichier,
            "url_view": f"http://localhost:8001/documents/{nom_fichier}"
        }

    except Exception as e:
        print(f" Erreur dans /import : {str(e)}")
        return {"reponse": f"Erreur lors de l'import : {str(e)}"}
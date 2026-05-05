# Imports standard
import os

# Imports tiers

from fastapi import APIRouter, Form, UploadFile, File, BackgroundTasks
from langchain_chroma import Chroma
from dotenv import load_dotenv

# Imports locaux
from library.ingest import ingest_file_to_db
from config import CHROMA_CLIENT, COLLECTION_NAME, EMBEDDINGS, UPLOAD_DIR

load_dotenv()
router = APIRouter()



@router.post("/import")
async def import_file(
    background_tasks: BackgroundTasks,
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

        db = Chroma(
            client=CHROMA_CLIENT, 
            collection_name=COLLECTION_NAME, 
            embedding_function=EMBEDDINGS
        )
        existing = db.get(where={"source": nom_fichier})

        if existing and len(existing["ids"]) > 0:
            print(f"Déjà indexé ({len(existing['ids'])} chunks). Ingestion ignorée.")
            return {
                "reponse": "Document déjà connu, prêt à être interrogé !",
                "filename": nom_fichier,
                "url_view": f"http://localhost:8001/documents/{nom_fichier}"
            }
        else:
            background_tasks.add_task(ingest_file_to_db, file_path, use_ocr=True)
            print(f"Tâche d'ingestion enregistrée en arrière-plan pour : {nom_fichier}")
            return {
                    "reponse": "Document reçu, analyse en cours...",
                    "filename": nom_fichier,
                    "url_view": f"http://localhost:8001/documents/{nom_fichier}"
        }



    except Exception as e:
        print(f" Erreur dans /import : {str(e)}")
        return {"reponse": f"Erreur lors de l'import : {str(e)}"}
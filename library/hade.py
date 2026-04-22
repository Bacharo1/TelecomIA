import os

# Imports tiers
import ollama
from fastapi import APIRouter, Form
from dotenv import load_dotenv

# Imports locaux
from library.ingest import ingest_file_to_db
from langchain_chroma import Chroma
from config import UPLOAD_DIR

from config import CHROMA_CLIENT, COLLECTION_NAME, EMBEDDINGS

load_dotenv()
router = APIRouter()



@router.post("/interroger")
async def interroger_document(
    existing_file: str = Form(...), 
    question: str = Form(None),
    mode: str = Form("chat")
):
    """
    Endpoint pour interroger un document existant.
    - Requiert un fichier déjà importé (existing_file).
    - Effectue une recherche dans ChromaDB et génère une réponse.
    """
    nom_fichier = existing_file
    file_path = os.path.join(UPLOAD_DIR, nom_fichier)

    try:
        # --- 1. Vérification du fichier ---
        if not os.path.exists(file_path):
            return {"reponse": f"Erreur : Le fichier {nom_fichier} n'existe pas."}


        # --- 3. Recherche dans ChromaDB ---
        db = Chroma(
            client=CHROMA_CLIENT,
            collection_name=COLLECTION_NAME,
            embedding_function=EMBEDDINGS
        )
        search_kwargs = {"filter": {"source": file_path}}

        # --- 4. Construction du prompt ---
        if mode == "resume":
            docs = db.similarity_search("Résumé global", k=6, **search_kwargs)
            contexte = "\n".join([d.page_content for d in docs])
            prompt = f"Fais un résumé structuré et synthétique du document **{nom_fichier}** :\n\n{contexte[:6000]}"
        else:  # mode "chat"
            if not question:
                return {"reponse": "Erreur : Posez une question."}
            docs = db.similarity_search(question, k=4, **search_kwargs)
            contexte = "\n---\n".join([d.page_content for d in docs])
            prompt = f"""
            CONTEXTE (Source: {nom_fichier}) :
            {contexte}

            QUESTION : {question}

            Réponds de manière précise et structurée en t'appuyant sur le contexte.
            """

        # --- 5. Génération de la réponse ---
        reponse = ollama.generate(model=os.getenv("OLLAMA_MODEL", "mistral"), prompt=prompt)

        return {
            "reponse": reponse['response'],
            "filename": nom_fichier,
            "url_view": f"http://localhost:8001/documents/{nom_fichier}"
        }

    except Exception as e:
        print(f" Erreur dans /interroger : {str(e)}")
        return {"reponse": f"Erreur serveur : {str(e)}"}
    

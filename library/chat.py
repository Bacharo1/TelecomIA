import os
import time
# Imports tiers
import ollama
from fastapi import APIRouter, Form
from dotenv import load_dotenv

# Imports locaux
from langchain_chroma import Chroma
from config import CHROMA_CLIENT, COLLECTION_NAME, EMBEDDINGS, UPLOAD_DIR
from customlogger import logger



load_dotenv()
router = APIRouter()



@router.post("/interroger")
async def interroger_document(
    
    existing_file: str = Form(None), 
    question: str = Form(None),
    mode: str = Form("chat")
):
    
    start_total = time.time()

    nom_fichier = existing_file
    file_path = os.path.join(UPLOAD_DIR, nom_fichier)

    try:
        # --- 1. Vérification du fichier ---
        if not os.path.exists(file_path):
            return {"reponse": f"Erreur : Le fichier {nom_fichier} n'existe pas."}


        # --- 2. Recherche dans ChromaDB ---
        start_step = time.time()
        db = Chroma(
            client=CHROMA_CLIENT,
            collection_name=COLLECTION_NAME,
            embedding_function=EMBEDDINGS
        )
        # Vérification que le document est bien indexé
        check = db.get(where={"source": nom_fichier})
        if not check or len(check["ids"]) == 0:
            return {
                "Pret": False,
                "reponse": "Ce document est encore en cours d'indexation, veuillez patienter quelques instants avant de poser une question.",
                "filename": nom_fichier,
                "url_view": f"http://localhost:8001/documents/{nom_fichier}"
            }
        

        logger.info(f"Connexion ChromaDB en {time.time() - start_step:.2f}s")
        
        search_kwargs = {"filter": {"source": nom_fichier}}

        # --- 3. Construction du prompt ---
        start_step = time.time()
        if mode == "resume":
            docs = db.max_marginal_relevance_search("contenu principal du document", k=10, fetch_k=50, lambda_mult=0.3, **search_kwargs)
            contexte = "\n\n".join([d.page_content for d in docs])
            prompt = f"Fais un résumé structuré et synthétique du document **{nom_fichier}** :\n\n{contexte}"
        else:  # mode "chat"
            if not question:
                return {"reponse": "Erreur : Posez une question."}
            docs = db.similarity_search(question, k=8, **search_kwargs)
            logger.info(f"Nombre de chunks trouvés : {len(docs)}")
            contexte = "\n---\n".join([d.page_content for d in docs])
            prompt = f"""
            CONTEXTE (Source: {nom_fichier}) : {contexte}

            QUESTION : {question}

            Réponds de manière précise et structurée en t'appuyant sur le contexte.
            """

        logger.info(f"Recherche vectorielle en {time.time() - start_step:.2f}s")

        # --- 4. Génération de la réponse ---
        start_step = time.time()
        print(prompt)
        reponse = ollama.generate(model=os.getenv("OLLAMA_MODEL", "mistral-dev"), prompt=prompt)
        logger.info(f"Génération Ollama en {time.time() - start_step:.2f}s")
        logger.info(f"Finished /interroger pour {nom_fichier} en {time.time() - start_total:.2f}s total.")

        return {
            "reponse": reponse['response'],
            "filename": nom_fichier,
            "url_view": f"http://localhost:8001/documents/{nom_fichier}"
        }
        

    except Exception as e:
        logger.error(f" Erreur dans /interroger : {str(e)}")
        return {"reponse": f"Erreur serveur : {str(e)}"}
    

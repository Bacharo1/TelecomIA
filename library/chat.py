import os
import time

# Imports tiers
import emoji
import ollama
from fastapi import APIRouter, Form
from dotenv import load_dotenv

# Imports locaux
from langchain_chroma import Chroma
from config import CHROMA_CLIENT, COLLECTION_NAME, EMBEDDINGS, UPLOAD_DIR
from library.customlogger import logger



load_dotenv()
router = APIRouter()

def get_chunks_tries_par_page(db, nom_fichier: str) -> list:
    tous_docs = db.get(
        where={"source": nom_fichier},
        include=["documents", "metadatas"]
    )
    paires = list(zip(tous_docs["documents"], tous_docs["metadatas"]))
    triees = sorted(
        paires,
        key=lambda x: x[1].get("page_number") if x[1].get("page_number") is not None else x[1].get("page", 0)
    )
    return [doc for doc, _ in triees]


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
            chunks_ordonnes = get_chunks_tries_par_page(db, nom_fichier)
            contexte_complet = "\n\n".join([doc for doc in chunks_ordonnes])
            if len(contexte_complet) <= 20000: # Si le contexte complet est raisonnable, on l'utilise tel quel
                logger.info(f"[RESUME] Contexte complet utilisé ({len(contexte_complet)} chars)")
                contexte = contexte_complet
            else:
                docs = db.max_marginal_relevance_search("contenu principal du document", k=30, fetch_k=70, lambda_mult=0.5, **search_kwargs)
                contexte = "\n\n".join([d.page_content for d in docs])
            prompt = f"Fais un résumé structuré et synthétique du document **{nom_fichier}** :\n\n{contexte}"
        else:  # mode "chat"
            if not question:
                return {"reponse": "Erreur : Posez une question."}
            docs = db.similarity_search(question, k=25, **search_kwargs)
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
        reponse = ollama.chat(model=os.getenv("OLLAMA_MODEL"),messages=[{"role": "user", "content": prompt}])
        logger.info(f"Génération Ollama en {time.time() - start_step:.2f}s")
        logger.info(f"Finished /interroger pour {nom_fichier} en {time.time() - start_total:.2f}s total.")
        clean_text = emoji.replace_emoji(reponse['message']['content'], replace='')
        return {
            "reponse": clean_text,
            "filename": nom_fichier,
            "url_view": f"http://localhost:8001/documents/{nom_fichier}"
        }
        

    except Exception as e:
        logger.error(f" Erreur dans /interroger : {str(e)}")
        return {"reponse": f"Erreur serveur : {str(e)}"}
    

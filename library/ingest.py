import os
import uuid
import time
from langchain_chroma import Chroma
from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader, 
    UnstructuredPDFLoader  # Ajouté pour les images/graphiques
)
from langchain_text_splitters import RecursiveCharacterTextSplitter
from customlogger import logger

from config import CHROMA_CLIENT, COLLECTION_NAME, EMBEDDINGS, ingestion_status 


def ingest_file_to_db(file_path: str, use_ocr: bool = True):
    """
    Ingest files into ChromaDB. 
    Set use_ocr=True for PDFs with images/charts.
    """
    start_total = time.time()
    abs_path = os.path.abspath(file_path)
    source_name = os.path.basename(abs_path)
    ext = os.path.splitext(abs_path)[-1].lower()

    if not os.path.exists(abs_path):
        logger.error(f" File not found at: {abs_path}")
        return {"status": "error", "message": "File not found"}

    logger.info(f" Starting ingestion for: {source_name} (Mode OCR: {use_ocr})")
    try:
        # --- PHASE 1: LOADING ---
        start_step = time.time()
        
        if ext == ".pdf":
            if use_ocr:
                try:
                    # Stratégie 'hi_res' pour analyser le layout et extraire le texte des images/tables
                    loader = UnstructuredPDFLoader(
                        abs_path,
                        strategy="hi_res",  # Analyse les graphiques et images
                        infer_table_structure=True, # Tente de reconstruire les tableaux
                        languages=["fra"]
                    )
                    
                except Exception as ocr_err:
                    logger.warning(f" hi_res failed ({ocr_err}), falling back to PyPDFLoader")
                    loader = PyPDFLoader(abs_path)
                    
            else:
                loader = PyPDFLoader(abs_path)
                
        else:
            loader = TextLoader(abs_path, encoding='utf-8')
            
        raw_docs = loader.load()
        load_time = time.time() - start_step
        logger.info(f" Loaded {len(raw_docs)} units/pages in {load_time:.2f}s")
        for i, doc in enumerate(raw_docs):
            logger.info(f" Doc {i} — {len(doc.page_content)} chars — page: {doc.metadata.get('page', '?')}")
        # Tag Metadata
        for doc in raw_docs:
            # On utilise le chemin relatif "storage/pdfs/nom.pdf" pour matcher le main.py
            doc.metadata["source"] = source_name 
            doc.metadata["ingested_at"] = time.strftime("%Y-%m-%d %H:%M:%S")

        # --- PHASE 2: SPLITTING ---
        start_step = time.time()
        # On augmente un peu la taille pour garder le contexte des tableaux
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1200, chunk_overlap=150)
        chunks = text_splitter.split_documents(raw_docs)
        split_time = time.time() - start_step
        logger.info(f" Split into {len(chunks)} chunks in {split_time:.2f}s")
        
        # --- PHASE 3: EMBEDDING & SAVING ---
        start_step = time.time()
        db = Chroma(
            client=CHROMA_CLIENT, 
            collection_name=COLLECTION_NAME, 
            embedding_function=EMBEDDINGS
        )
        
        db.add_documents(chunks, ids=[str(uuid.uuid4()) for _ in chunks])
        db_time = time.time() - start_step
        logger.info(f" Saved to ChromaDB in {db_time:.2f}s")

        total_time = time.time() - start_total
        logger.info(f" Finished {source_name} en {total_time:.2f}s total.")
        ingestion_status[source_name] = True
        return {
            "status": "success",
            "file": source_name,
            "total_delay": f"{total_time:.2f}s",
            "chunks": len(chunks)
        }

    except Exception as e:
        logger.error(f" Failed to ingest {source_name}: {str(e)}")
        return {"status": "error", "message": str(e)}
    
    

# ingest_file_to_db(r"docs/Presentation_RGPD.pdf", use_ocr=True)
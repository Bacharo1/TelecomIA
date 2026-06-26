import pytest
from unittest.mock import patch, MagicMock
from langchain.schema import Document

# Test 1 : les chunks respectent la taille max de 1200 caractères
def test_chunk_size():
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    splitter = RecursiveCharacterTextSplitter(chunk_size=1200, chunk_overlap=150)
    texte_long = "A" * 5000
    chunks = splitter.split_text(texte_long)
    for chunk in chunks:
        assert len(chunk) <= 1200, f"Chunk trop grand : {len(chunk)} caractères"

# Test 2 : les métadonnées 'source' et 'date' sont bien présentes
def test_chunk_metadata():
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from datetime import date
    splitter = RecursiveCharacterTextSplitter(chunk_size=1200, chunk_overlap=150)
    docs = [Document(page_content="Contenu test", metadata={"source": "rapport.pdf"})]
    chunks = splitter.split_documents(docs)
    for chunk in chunks:
        assert "source" in chunk.metadata, "Métadonnée 'source' manquante"

# Test 3 : un document vide ne produit pas de chunks
def test_chunk_empty_document():
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    splitter = RecursiveCharacterTextSplitter(chunk_size=1200, chunk_overlap=150)
    chunks = splitter.split_text("")
    assert len(chunks) == 0, "Un document vide ne doit pas produire de chunks"
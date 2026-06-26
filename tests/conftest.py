"""
Fixtures partagees pour les tests TelecomIA (critere C12).

Deux familles de fixtures :
- mock_* : isolent completement Chroma/Ollama -> tests unitaires rapides,
  utiles pour valider la PLOMBERIE (routing, format JSON, contrats d'interface).
- chroma_reelle / pdf_test_reel : utilisent une vraie instance ChromaDB locale
  (docker compose up) et un vrai PDF -> tests d'INTEGRATION, utiles pour valider
  que la recherche vectorielle retrouve reellement le bon contenu.

Les tests d'integration sont automatiquement skippes si ChromaDB n'est pas
joignable, pour ne jamais faire echouer le run faute d'environnement lance.
"""

import os
import shutil
import socket
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from main import app

FIXTURES_DIR = Path(__file__).parent / "fixtures"
TEST_PDF_PATH = FIXTURES_DIR / "test_doc.pdf"

CHROMA_HOST = os.getenv("CHROMA_HOST", "localhost")
CHROMA_PORT = int(os.getenv("CHROMA_PORT", "8000"))


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _chroma_disponible(host: str = CHROMA_HOST, port: int = CHROMA_PORT, timeout: float = 1.0) -> bool:
    """Teste si ChromaDB repond sur host:port (utilise pour le skip auto)."""
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


# ---------------------------------------------------------------------------
# Fixtures generiques
# ---------------------------------------------------------------------------

@pytest.fixture
def client():
    """Client de test FastAPI (TestClient) sur l'app reelle de main.py."""
    return TestClient(app)


@pytest.fixture
def pdf_test_reel(tmp_path):
    """
    Copie le PDF de test dans un dossier temporaire et retourne son chemin.
    Genere le fichier au besoin (voir fixtures/generate_test_pdf.py).

    Le module est charge par chemin de fichier (importlib) plutot que par
    "import fixtures...", pour ne pas dependre de la presence de "fixtures"
    dans sys.path (qui varie selon comment pytest est lance).
    """
    if not TEST_PDF_PATH.exists():
        import importlib.util

        script_path = FIXTURES_DIR / "generate_test_pdf.py"
        spec = importlib.util.spec_from_file_location("generate_test_pdf", script_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        module.generate()

    dest = tmp_path / "test_doc.pdf"
    shutil.copy(TEST_PDF_PATH, dest)
    return dest


# ---------------------------------------------------------------------------
# Fixtures MOCKEES (tests unitaires d'interface / logique isolee)
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_chroma(mocker):
    """
    Mock de la collection ChromaDB utilisee dans library/chat.py.
    Simule le format reel retourne par .query() : top chunks + metadonnees
    'source' (utilisees pour le filtrage par document).
    """
    mock = mocker.patch("library.chat.collection")
    mock.query.return_value = {
        "documents": [["Contenu du chunk 1 sur test.pdf", "Contenu du chunk 2 sur test.pdf"]],
        "metadatas": [[{"source": "test.pdf"}, {"source": "test.pdf"}]],
    }
    return mock


@pytest.fixture
def mock_ollama_generate(mocker):
    """Mock de ollama.generate() utilise dans library/chat.py."""
    mock = mocker.patch("library.chat.ollama.generate")
    mock.return_value = {"response": "<p>Reponse generee par le modele.</p>"}
    return mock


# ---------------------------------------------------------------------------
# Fixtures REELLES (tests d'integration -- necessitent docker compose up)
# ---------------------------------------------------------------------------

@pytest.fixture
def chroma_disponible():
    """Booleen reutilisable si un test veut decider lui-meme quoi faire."""
    return _chroma_disponible()


@pytest.fixture
def skip_si_chroma_absente():
    """
    A utiliser dans les tests d'integration : skip proprement si ChromaDB
    n'est pas joignable, plutot que de planter le run pytest.
    """
    if not _chroma_disponible():
        pytest.skip(
            f"ChromaDB non joignable sur {CHROMA_HOST}:{CHROMA_PORT} "
            "(lancer 'docker compose up -d' pour activer les tests d'integration)"
        )


@pytest.fixture
def collection_test_reelle(skip_si_chroma_absente):
    """
    Cree (ou recupere) une collection ChromaDB DEDIEE aux tests, distincte
    de 'mistral_kb' utilisee en production, pour ne jamais polluer les
    donnees reelles. Nettoyee automatiquement apres le test.
    """
    import chromadb

    client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
    nom_collection = "test_c12_collection"

    # Nettoyage prealable si un run precedent a echoue avant le teardown
    try:
        client.delete_collection(nom_collection)
    except Exception:
        pass

    collection = client.create_collection(nom_collection)
    yield collection

    try:
        client.delete_collection(nom_collection)
    except Exception:
        pass
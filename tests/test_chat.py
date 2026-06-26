import pytest

# Test 4 : la recherche vectorielle retourne au moins 1 chunk
def test_recherche_retourne_des_chunks(mock_chroma):
    result = mock_chroma.query(
        query_texts=["Question test"],
        n_results=25,
        where={"source": "test.pdf"}
    )
    docs = result["documents"][0]
    assert len(docs) >= 1, "La recherche doit retourner au moins 1 chunk"

# Test 5 : la réponse Ollama n'est pas vide
def test_generation_ollama_non_vide(mock_ollama):
    result = mock_ollama(model="gemma4", prompt="Contexte : ... Question : test")
    assert result["response"] != "", "La réponse Ollama ne doit pas être vide"
    assert isinstance(result["response"], str), "La réponse doit être une chaîne"

# Test 6 : l'endpoint /interroger répond 200 avec les bons champs
def test_endpoint_interroger(client, mock_chroma, mock_ollama):
    response = client.post("/interroger", json={
        "question": "Quel est l'objet du document ?",
        "existing_file": "test.pdf"
    })
    assert response.status_code == 200
    data = response.json()
    assert "reponse" in data, "La réponse JSON doit contenir 'reponse'"
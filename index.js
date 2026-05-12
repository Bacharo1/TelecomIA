const API_URL = "http://localhost:8001";

// --- ELEMENTS HTML ---
const pdfFileInput = document.getElementById('pdfFile');
const questionInput = document.getElementById('question');
const btnEnvoyer = document.getElementById('btnEnvoyer');
const btnResume = document.getElementById('btnResume');
const btnImport = document.getElementById('btnImport');
const btnReset = document.getElementById('btnReset');
const chatBox = document.getElementById('chatBox');
const listeDocs = document.getElementById('listeDocs');
const pdfViewer = document.getElementById('pdfViewer');
const progressContainer = document.getElementById('progress-container');
const progressBar = document.getElementById('upload-progress');
const progressPercent = document.getElementById('progress-percent');


let fichierSelectionne = null;

// --- FONCTION POUR AJOUTER UN MESSAGE AU CHAT ---
function ajouterMessage(role, texte) {
    const div = document.createElement('div');
    div.className = role === 'user' ? 'user-msg' : 'ai-msg';
    div.innerHTML = `<b>${role === 'user' ? 'Vous' : 'TelecomIA'}:</b> ${texte}`;
    chatBox.appendChild(div);
    
    // Scroll automatique fluide
    chatBox.scrollTo({
        top: chatBox.scrollHeight,
        behavior: 'smooth'
    });
}
const interrogerDocument = async (formData) => {
    // Sélection des éléments
    const progressContainer = document.getElementById('progress-container');
    const progressBar = document.getElementById('upload-progress');
    const progressPercent = document.getElementById('progress-percent');

    // 1. AFFICHER LE BLOC (début de l'upload)
    progressContainer.style.display = 'block';
    btnImport.style.display = 'none';
    progressBar.value = 0;
    progressPercent.innerText = "0%";

    // Simulation de progression (jusqu'à 90%)
    let currentProgress = 0;
    const interval = setInterval(() => {
        if (currentProgress < 90) {
            currentProgress += (90 - currentProgress) * 0.03;
            progressBar.value = currentProgress;
            progressPercent.innerText = `${Math.round(currentProgress)}%`;
        }
    }, 200);

    try {
        const mode = formData.get("mode"); 
        const route = (mode === "import") ? "/import" : "/interroger";

        const response = await fetch(`${API_URL}${route}`, {
            method: "POST",
            body: formData
        });

        if (!response.ok) throw new Error("Erreur serveur");

        // 2. SUCCÈS : PASSER À 100%
        clearInterval(interval);
        progressBar.value = 100;
        progressPercent.innerText = "100% - Terminé";

        const result = await response.json();
        
        // 3. CACHER APRÈS 2 SECONDES
        setTimeout(() => {
            progressContainer.style.display = 'none';
            btnImport.style.display = 'inline-block';
            // Réinitialisation pour le prochain upload
            progressBar.value = 0;
            progressPercent.innerText = "0%";
        }, 2000); // 2000 ms = 2 secondes

        return result;

    } catch (error) {
        clearInterval(interval);
        console.error("Erreur:", error);
        // En cas d'erreur, on cache souvent plus vite ou on affiche un message d'erreur
        setTimeout(() => { progressContainer.style.display = 'none'; 
        btnImport.style.display = 'inline-block'; }, 500); throw error;
    }
};


// --- FONCTION PRINCIPALE : INTERROGER ---
async function envoyerRequete(mode = "chat") {
    console.log("=== envoyerRequete appelée, mode:", mode); // ← ajoute ça
    console.log("file:", pdfFileInput.files[0]);
    console.log("fichierSelectionne:", fichierSelectionne);
    console.log("btnImport.disabled:", btnImport.disabled);
    btnImport.disabled = true; // Empêche le double-clic
    const file = pdfFileInput.files[0];
    const question = questionInput.value;
     
    if (!file && !fichierSelectionne){ return alert("Veuillez d'abord sélectionner un PDF.");}
    if (mode === "chat" && !question){ return alert("Posez une question.");}
    btnImport.disabled = true;
    if (mode === "chat") questionInput.value = "";
     

    const formData = new FormData();
    
    if (file) {
        formData.append("file", file);
    } else {
        formData.append("existing_file", fichierSelectionne);
    }
         

    formData.append("question", mode === "resume" ? "Fais un résumé synthétique du document." : question);
    formData.append("mode", mode);

    if (mode === "import") {
        ajouterMessage('ai', "Analyse du document en cours...");
    } else {
        ajouterMessage('user', mode === "resume" ? "Demande de résumé..." : question);
    }
         

    
    interrogerDocument(formData).then(data => {
        if (mode === "import") {
             if (data.filename) {
            fichierSelectionne = data.filename;
            pdfFileInput.value = "";
            ajouterMessage('ai', "Fichier reçu, indexation en cours...")
        }

        const attente = setInterval(async () => {


            const res = await fetch(`${API_URL}/status/${encodeURIComponent(data.filename)}`);

            const json = await res.json();

            if (json.pret !== false) {
                clearInterval(attente);
                ajouterMessage('ai', " Document prêt ! Que voulez-vous savoir ?");
                btnImport.disabled = false;
                chargerListe();
            }
        }, 5000);
    } else {
        ajouterMessage('ai', data.reponse);
        if (data.filename) {
            fichierSelectionne = data.filename;
            pdfFileInput.value = "";
        }
        btnImport.disabled = false;
    }

        
             

    }, error => {
        console.error("Erreur lors de l'interrogation:", error);
        ajouterMessage('ai', "Erreur lors de l'import du document.");
        
        btnImport.disabled = false;
    });
}



// --- CHARGER LA LISTE DES DOCUMENTS ---
async function chargerListe() {
    try {
        const res = await fetch(`${API_URL}/liste-documents`);
        const data = await res.json();
        listeDocs.innerHTML = "";
         
        data.documents.forEach(doc => {
            const li = document.createElement('li');
            li.textContent = doc;
            
            // Persistance de l'état actif lors du rafraîchissement
            if (fichierSelectionne === doc) {
                li.classList.add('actif');
            }

            li.onclick = () => {
                fichierSelectionne = doc;
                
                // UX : On vide l'input file pour éviter toute confusion
                pdfFileInput.value = ""; 
                
                pdfViewer.innerHTML = "";
                
                // Utilisation de la classe CSS .actif (plus propre)
                document.querySelectorAll('#listeDocs li').forEach(el => el.classList.remove('actif'));
                li.classList.add('actif');

                const urlApercu = data.url_view || `${API_URL}/documents/${doc}`;
                pdfViewer.innerHTML = `<embed src="${urlApercu}" width="100%" height="100%" type="application/pdf">`;
            };
            listeDocs.appendChild(li);
        });
             

    } catch (error) {
        listeDocs.innerHTML = "<li style='color: red;'>Erreur de chargement des documents</li>";
        console.error("Erreur chargement liste:", error);
    }
}

///--- FONCTION DE RÉINITIALISATION DE LA SESSION ---

async function reset() {
    btnReset.disabled = true; // Désactive le bouton pendant la requête
    btnReset.textContent = "Réinitialisation...";

    try {
        const response = await fetch(`${API_URL}/clear-session`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });

        if (response.ok) {
            alert("L'IA a oublié les documents précédents !");
            // Optionnel : recharger la page pour rafraîchir l'affichage
            window.location.reload();
        } else {
            throw new Error("La requête n'a pas abouti.");
        }
    } catch (error) {
        console.error("Erreur lors de la réinitialisation:", error);
        alert("Erreur lors de la réinitialisation de la session.");
    } finally {
        btnReset.disabled = false; // Réactive le bouton après la requête
        btnReset.textContent = "Réinitialiser";
    }
}


// --- ÉVÉNEMENTS ---
btnEnvoyer.onclick = () => envoyerRequete("chat");
btnResume.onclick = () => envoyerRequete("resume");
btnImport.onclick = () => envoyerRequete("import");
btnReset.onclick = () => reset();

questionInput.onkeypress = (e) => {
    if (e.key === 'Enter') envoyerRequete("chat");
};

// Initialisation
chargerListe();